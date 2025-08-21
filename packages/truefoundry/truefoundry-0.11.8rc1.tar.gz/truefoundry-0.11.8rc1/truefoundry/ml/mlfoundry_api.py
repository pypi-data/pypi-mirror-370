import os
import time
import uuid
import zipfile
from io import BytesIO
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import coolname
from truefoundry_sdk import Collaborator, MlRepoManifest, NotFoundError
from truefoundry_sdk.core import ApiError

from truefoundry import client
from truefoundry.common.utils import ContextualDirectoryManager
from truefoundry.ml import constants
from truefoundry.ml._autogen.client import (  # type: ignore[attr-defined]
    ArtifactDto,
    ArtifactType,
    CreateDatasetRequestDto,
    CreateRunRequestDto,
    DatasetDto,
    ExperimentsApi,
    ExportDeploymentFilesRequestDto,
    ListArtifactsRequestDto,
    ListArtifactVersionsRequestDto,
    ListDatasetsRequestDto,
    ListModelVersionsRequestDto,
    MlfoundryArtifactsApi,
    ModelDto,
    ModelServer,
    ModelVersionEnvironment,
    RunsApi,
    RunTagDto,
    SearchRunsRequestDto,
)
from truefoundry.ml._autogen.client.exceptions import (
    ApiException,
    NotFoundException,
)
from truefoundry.ml.enums import ModelFramework, ViewType
from truefoundry.ml.exceptions import MlFoundryException
from truefoundry.ml.internal_namespace import NAMESPACE
from truefoundry.ml.log_types.artifacts.artifact import (
    ArtifactPath,
    ArtifactVersion,
    BlobStorageDirectory,
)
from truefoundry.ml.log_types.artifacts.dataset import DataDirectory
from truefoundry.ml.log_types.artifacts.general_artifact import _log_artifact_version
from truefoundry.ml.log_types.artifacts.model import (
    ModelVersion,
    _log_model_version,
)
from truefoundry.ml.logger import logger
from truefoundry.ml.mlfoundry_run import MlFoundryRun
from truefoundry.ml.session import (
    MLFoundrySession,
    _get_api_client,
)
from truefoundry.ml.validation_utils import (
    _validate_ml_repo_description,
    _validate_ml_repo_name,
    _validate_run_name,
)

if TYPE_CHECKING:
    from truefoundry.ml import ModelFrameworkType

_SEARCH_MAX_RESULTS_DEFAULT = 1000
_ML_FOUNDRY_API_REQUEST_TIMEOUT = 10
_INTERNAL_ENV_VARS = [
    "TFY_INTERNAL_APPLICATION_ID",
    "TFY_INTERNAL_JOB_RUN_NAME",
]


def _get_internal_env_vars_values() -> Dict[str, str]:
    env = {}
    for env_var_name in _INTERNAL_ENV_VARS:
        value = os.getenv(env_var_name)
        if value:
            env[env_var_name] = value

    return env


def _resolve_version(version: Union[int, str]) -> int:
    if not isinstance(version, int) and not (
        isinstance(version, str) and version.isnumeric()
    ):
        raise MlFoundryException(
            f"version must be an integer or string containing numbers only. Got {version!r}"
        )
    final_version = int(version)
    if final_version <= 0:
        raise ValueError("version must be greater than 0")
    return final_version


class MlFoundry:
    """MlFoundry."""

    # TODO (chiragjn): Don't allow session as None here!
    def __init__(self, session: MLFoundrySession):
        """__init__

        Args:
            session (Optional[Session], optional): Session instance to get auth credentials from
        """
        self._api_client = _get_api_client(session=session)
        self._experiments_api = ExperimentsApi(api_client=self._api_client)
        self._runs_api = RunsApi(api_client=self._api_client)
        self._mlfoundry_artifacts_api = MlfoundryArtifactsApi(
            api_client=self._api_client
        )

    def _get_ml_repo_id(self, ml_repo: str) -> str:
        """_get_ml_repo_id.

        Args:
            ml_repo (str): The name of the ML Repo.

        Returns:
            str: The id of the ML Repo.
        """
        try:
            result = list(client.ml_repos.list(name=ml_repo, limit=1))
            ml_repo_instance = result[0]
        except (IndexError, NotFoundError):
            err_msg = (
                f"ML Repo Does Not Exist for name: {ml_repo}. You may either "
                f"create it from the dashboard or using "
                f"`client.create_ml_repo(ml_repo='{ml_repo}', storage_integration_fqn='<storage_integration_fqn>')`"
            )
            raise MlFoundryException(err_msg) from None
        except ApiError as e:
            err_msg = (
                f"Error happened in getting ML Repo based on name: "
                f"{ml_repo}. Error details: {e}"
            )
            raise MlFoundryException(err_msg) from e
        return ml_repo_instance.id

    def list_ml_repos(self) -> List[str]:
        """Returns a list of names of ML Repos accessible by the current user.

        Returns:
            List[str]: A list of names of ML Repos
        """
        # TODO (chiragjn): This API should yield ML Repo Entities instead of just names
        #   Kinda useless without it
        ml_repos_names = []
        max_results = 25
        try:
            for ml_repo_instance in client.ml_repos.list(limit=max_results):
                if ml_repo_instance.id != "0":
                    ml_repos_names.append(ml_repo_instance.manifest.name)
        except ApiError as e:
            err_msg = f"Error happened in fetching ML Repos. Error details: {e}"
            raise MlFoundryException(err_msg) from e
        return ml_repos_names

    def create_ml_repo(
        self,
        name: str,
        storage_integration_fqn: str,
        description: Optional[str] = None,
    ):
        """Creates an ML Repository.

        Args:
            name (str): The name of the Repository you want to create.
            storage_integration_fqn(str): The storage integration FQN to use for the experiment
                for saving artifacts.
            description (str): A description for ML Repo.

        Examples:

            ### Create Repository
            ```python
            from truefoundry.ml import get_client

            client = get_client()

            client.create_ml_repo(
                ml_repo="my-repo",
                # This controls which bucket is used.
                # You can get this from Platform > Integrations > Copy FQN of any Blob Storage type integration.
                storage_integration_fqn="..."
            )
            ```
        """
        _validate_ml_repo_name(ml_repo_name=name)
        if description:
            _validate_ml_repo_description(description=description)
        try:
            result = list(client.ml_repos.list(name=name, limit=1))
            existing_ml_repo = result[0]
        except (IndexError, NotFoundError):
            existing_ml_repo = None
        except ApiError as e:
            err_msg = (
                f"Error happened in getting ML Repo based on name: "
                f"{name}. Error details: {e}"
            )
            raise MlFoundryException(err_msg) from e

        if not existing_ml_repo:
            session = client._get_session()
            user_info = session.user_info
            if not user_info.email:
                raise MlFoundryException(
                    "Virtual accounts cannot be used to create new ML Repos"
                )
            try:
                client.ml_repos.create_or_update(
                    manifest=MlRepoManifest(
                        name=name,
                        description=description,
                        storage_integration_fqn=storage_integration_fqn,
                        collaborators=[
                            Collaborator(
                                subject=f"user:{user_info.email}",
                                role_id="mlf-project-admin",
                            )
                        ],
                    ),
                )
            except ApiError as e:
                err_msg = f"Error happened in creating ML Repo with name: {name}. Error details: {e}"
                raise MlFoundryException(err_msg) from e
            return

        if existing_ml_repo.manifest.storage_integration_fqn != storage_integration_fqn:
            raise MlFoundryException(
                f"ML Repo with same name already exists with storage integration:"
                f"{existing_ml_repo.manifest.storage_integration_fqn!r}. "
                f"Cannot update the storage integration to: {storage_integration_fqn!r}"
            )

    def create_run(
        self,
        ml_repo: str,
        run_name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> MlFoundryRun:
        """Initialize a `run`.

        In a machine learning experiment `run` represents a single experiment
        conducted under a ML Repo.
        Args:
            ml_repo (str): The name of the ML Repo under which the run will be created.
                ml_repo should only contain alphanumerics (a-z,A-Z,0-9) or hyphen (-).
                The user must have `ADMIN` or `WRITE` access to this ML Repo.
            run_name (Optional[str], optional): The name of the run. If not passed, a randomly
                generated name is assigned to the run. Under a ML Repo, all runs should have
                a unique name. If the passed `run_name` is already used under a ML Repo, the
                `run_name` will be de-duplicated by adding a suffix.
                run name should only contain alphanumerics (a-z,A-Z,0-9) or hyphen (-).
            tags (Optional[Dict[str, Any]], optional): Optional tags to attach with
                this run. Tags are key-value pairs.
            kwargs:

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.

        Examples:

            ### Create a run under current user.
            ```python
            from truefoundry.ml import get_client

            client = get_client()

            tags = {"model_type": "svm"}
            run = client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel", tags=tags
            )

            run.end()
            ```

            ### Creating a run using context manager.
            ```python
            from truefoundry.ml import get_client

            client = get_client()
            with client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel"
            ) as run:
                # ...
                # Model training code
                ...
            # `run` will be automatically marked as `FINISHED` or `FAILED`.
            ```

            ### Create a run in a ML Repo owned by a different user.
            ```python
            from truefoundry.ml import get_client

            client = get_client()

            tags = {"model_type": "svm"}
            run = client.create_run(
                ml_repo="my-classification-project",
                run_name="svm-with-rbf-kernel",
                tags=tags,
            )
            run.end()
            ```
        """
        if not run_name:
            run_name = coolname.generate_slug(2)
            logger.info(
                f"No run_name given. Using a randomly generated name {run_name}."
                " You can pass your own using the `run_name` argument"
            )
        _validate_run_name(name=run_name)
        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        if tags is not None:
            NAMESPACE.validate_namespace_not_used(tags.keys())
        else:
            tags = {}

        tags.update(_get_internal_env_vars_values())
        _run = self._runs_api.create_run_post(
            CreateRunRequestDto(
                start_time=int(
                    time.time() * 1000
                ),  # TODO (chiragjn): computing start time should be on server side!
                experiment_id=ml_repo_id,
                name=run_name,
                tags=[RunTagDto(key=k, value=v) for k, v in tags.items()],
            )
        )
        run = _run.run
        mlf_run_id = run.info.run_id
        kwargs.setdefault("auto_end", True)
        mlf_run = MlFoundryRun(experiment_id=ml_repo_id, run_id=mlf_run_id, **kwargs)
        mlf_run._add_git_info()
        mlf_run._add_python_truefoundry_version()
        logger.info(f"Run {run.info.fqn!r} has started.")
        logger.info(f"Link to the dashboard for the run: {mlf_run.dashboard_link}")
        return mlf_run

    def get_run_by_id(self, run_id: str) -> MlFoundryRun:
        """Get an existing `run` by the `run_id`.

        Args:
            run_id (str): run_id or fqn of an existing `run`.

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.

        Examples:

            ### Get run by the run id
            ```python
            from truefoundry.ml import get_client

            client = get_client()

            run = client.get_run_by_id(run_id='a8f6dafd70aa4baf9437a33c52d7ee90')
            ```
        """
        if run_id == "" or (not isinstance(run_id, str)):
            raise MlFoundryException(
                f"run_id must be string type and not empty. "
                f"Got {type(run_id)} type with value {run_id}"
            )
        if "/" in run_id:
            return self.get_run_by_fqn(run_id)
        _run = self._runs_api.get_run_get(run_id=run_id)
        run = _run.run
        mlfoundry_run = MlFoundryRun._from_dto(run)
        logger.info(
            f"Link to the dashboard for the run: {mlfoundry_run.dashboard_link}"
        )
        return mlfoundry_run

    def get_run_by_fqn(self, run_fqn: str) -> MlFoundryRun:
        """Get an existing `run` by `fqn`.

        `fqn` stands for Fully Qualified Name. A run `fqn` has the following pattern:
        tenant_name/ml_repo/run_name

        If  a run `svm` under the ML Repo `cat-classifier` in `truefoundry` tenant,
        the `fqn` will be `truefoundry/cat-classifier/svm`.

        Args:
            run_fqn (str): `fqn` of an existing run.

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.

        Examples:

            ### get run by run fqn
            ```python
            from truefoundry.ml import get_client

            client = get_client()

            run = client.get_run_by_fqn(run_fqn='truefoundry/my-repo/svm')
            ```
        """
        _run = self._runs_api.get_run_by_fqn_get(run_fqn=run_fqn)
        run = _run.run
        mlfoundry_run = MlFoundryRun._from_dto(run)
        logger.info(
            f"Link to the dashboard for the run: {mlfoundry_run.dashboard_link}"
        )
        return mlfoundry_run

    def get_run_by_name(
        self,
        ml_repo: str,
        run_name: str,
    ) -> MlFoundryRun:
        """Get an existing `run` by `run_name`.

        Args:
            ml_repo (str): name of the ml_repo of which the run is part of.
            run_name (str): the name of the run required

        Returns:
            MlFoundryRun: An instance of `MlFoundryRun` class which represents a `run`.

        Examples:

            ### get run by name
            ```python
            from truefoundry.ml import get_client

            client = get_client()

            run = client.get_run_by_name(run_name='svm', ml_repo='my-repo')
            ```
        """
        _run = self._runs_api.get_run_by_name_get(
            experiment_id=None,
            run_name=run_name,
            experiment_name=ml_repo,
        )
        run = _run.run
        mlfoundry_run = MlFoundryRun._from_dto(run)
        logger.info(
            f"Link to the dashboard for the run: {mlfoundry_run.dashboard_link}"
        )
        return mlfoundry_run

    def search_runs(
        self,
        ml_repo: str,
        filter_string: str = "",
        run_view_type: ViewType = ViewType.ACTIVE_ONLY.value,
        order_by: Sequence[str] = ("attribute.start_time DESC",),
        job_run_name: Optional[str] = None,
    ) -> Iterator[MlFoundryRun]:
        """
        The user must have `READ` access to the ML Repo.
        Returns an iterator that returns a MLFoundryRun on each next call.
        All the runs under a ML Repo which matches the filter string and the run_view_type are returned.

        Args:
            ml_repo (str): Name of the ML Repo.
            filter_string (str, optional):
                Filter query string, defaults to searching all runs.
                Identifier required in the LHS of a search expression.
                Signifies an entity to compare against. An identifier has two parts separated by a period: the
                type of the entity and the name of the entity.
                The type of the entity is metrics, params, attributes, or tags.
                The entity name can contain alphanumeric characters and special characters.
                You can search using two run attributes : status and artifact_uri. Both attributes have string values.
                When a metric, parameter, or tag name contains a special character like hyphen, space, period,
                and so on, enclose the entity name in double quotes or backticks,
                params."model-type" or params.`model-type`

            run_view_type (str, optional): one of the following values "ACTIVE_ONLY", "DELETED_ONLY", or "ALL" runs.
            order_by (List[str], optional):
                List of columns to order by (e.g., "metrics.rmse"). Currently supported values
                are metric.key, parameter.key, tag.key, attribute.key. The ``order_by`` column
                can contain an optional ``DESC`` or ``ASC`` value. The default is ``ASC``.
                The default ordering is to sort by ``start_time DESC``.

            job_run_name (str): Name of the job which are associated with the runs to get that runs

        Returns:
            Iterator[MlFoundryRun]: MLFoundryRuns matching the search query.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            with client.create_run(ml_repo="my-project", run_name="run-1") as run1:
                run1.log_metrics(metric_dict={"accuracy": 0.74, "loss": 0.6})
                run1.log_params({"model": "LogisticRegression", "lambda": "0.001"})

            with client.create_run(ml_repo="my-project", run_name="run-2") as run2:
                run2.log_metrics(metric_dict={"accuracy": 0.8, "loss": 0.4})
                run2.log_params({"model": "SVM"})

            # Search for the subset of runs with logged accuracy metric greater than 0.75
            filter_string = "metrics.accuracy > 0.75"
            runs = client.search_runs(ml_repo="my-project", filter_string=filter_string)

            # Search for the subset of runs with logged accuracy metric greater than 0.7
            filter_string = "metrics.accuracy > 0.7"
            runs = client.search_runs(ml_repo="my-project", filter_string=filter_string)

            # Search for the subset of runs with logged accuracy metric greater than 0.7 and model="LogisticRegression"
            filter_string = "metrics.accuracy > 0.7 and params.model = 'LogisticRegression'"
            runs = client.search_runs(ml_repo="my-project", filter_string=filter_string)

            # Search for the subset of runs with logged accuracy metric greater than 0.7 and
            # order by accuracy in Descending order
            filter_string = "metrics.accuracy > 0.7"
            order_by = ["metric.accuracy DESC"]
            runs = client.search_runs(
                ml_repo="my-project", filter_string=filter_string, order_by=order_by
            )

            filter_string = "metrics.accuracy > 0.7"
            runs = client.search_runs(
                ml_repo="transformers", order_by=order_by ,job_run_name='job_run_name', filter_string=filter_string
            )

            order_by = ["metric.accuracy DESC"]
            runs = client.search_runs(
                ml_repo="my-project", filter_string=filter_string, order_by=order_by, max_results=10
            )
            ```
        """
        _validate_ml_repo_name(ml_repo_name=ml_repo)
        try:
            result = list(client.ml_repos.list(name=ml_repo, limit=1))
            ml_repo_instance = result[0]
        except (IndexError, NotFoundError):
            raise MlFoundryException(
                f"ML Repo with name {ml_repo} does not exist. "
                f"You may either create it from the dashboard or using "
                f"`client.create_ml_repo(ml_repo='{ml_repo}', storage_integration_fqn='<storage_integration_fqn>')`"
            ) from None
        except ApiError as e:
            raise MlFoundryException(
                f"ML Repo with name {ml_repo} does not exist or your user does not have permission to access it: {e}"
            ) from e

        ml_repo_id = ml_repo_instance.id

        page_token = None
        done = False
        if job_run_name:
            if filter_string == "":
                filter_string = f"tags.TFY_INTERNAL_JOB_RUN_NAME = '{job_run_name}'"
            else:
                filter_string += (
                    f" and tags.TFY_INTERNAL_JOB_RUN_NAME = '{job_run_name}'"
                )
        while not done:
            runs_page = self._runs_api.search_runs_post(
                SearchRunsRequestDto(
                    experiment_ids=[ml_repo_id],
                    filter=filter_string,
                    run_view_type=run_view_type,
                    max_results=_SEARCH_MAX_RESULTS_DEFAULT,
                    order_by=order_by,
                    page_token=page_token,
                )
            )
            runs = runs_page.runs
            page_token = runs_page.next_page_token

            for run in runs:
                yield MlFoundryRun._from_dto(run)
            if not runs or page_token is None:
                done = True

    def _initialize_model_server(
        self,
        name: str,
        model_version_fqn: str,
        workspace_fqn: str,
        model_server: ModelServer,
        output_dir: Optional[str] = None,
    ) -> str:
        """
        Initialize the model server for deployment.

        Args:
            name (str): Name of the application.
            model_version_fqn (str): Fully Qualified Name of the model version.
            workspace_fqn (str): Fully Qualified Name of the workspace.
            model_server (ModelServer): Server type for deployment (e.g., TRITON).
            output_dir (Optional[str]): Directory where the model files will be extracted.
                                        Defaults to the current working directory.

        Returns:
            str: Path to the directory where the model files are extracted.

        Raises:
            MlFoundryException: If an error occurs during API calls, directory creation, or file extraction.
        """

        # Using get_with_http_info to get the response object and extract the raw data
        try:
            export_deployment_files_request_dto = ExportDeploymentFilesRequestDto(
                model_version_fqn=model_version_fqn,
                workspace_fqn=workspace_fqn,
                service_name=name,
                model_server=model_server,
            )
            response = self._mlfoundry_artifacts_api.export_deployment_files_by_fqn_post_with_http_info(
                export_deployment_files_request_dto=export_deployment_files_request_dto,
                _preload_content=False,
                _request_timeout=_ML_FOUNDRY_API_REQUEST_TIMEOUT,
            )
        except ApiException as e:
            err_msg = (
                f"Failed to fetch deployment files for name={name}, "
                f"model_version_fqn={model_version_fqn}, workspace_fqn={workspace_fqn}. "
                f"Error: {e}"
            )
            raise MlFoundryException(err_msg) from e

        output_dir = os.path.abspath(output_dir or os.getcwd())
        codegen_dir = os.path.join(output_dir, name)
        if codegen_dir == output_dir:
            raise ValueError("Name cannot be empty, please provide a valid name")

        try:
            with ContextualDirectoryManager(dir_path=codegen_dir) as dir_path:
                with zipfile.ZipFile(BytesIO(response.raw_data), mode="r") as zip_file:
                    zip_file.extractall(dir_path)
        except FileExistsError as e:
            err_msg = (
                f"Deployment directory {codegen_dir!r} already exists. "
                "Please choose a different deployment name or delete the existing directory."
            )
            raise MlFoundryException(err_msg) from e
        except zipfile.BadZipFile as e:
            raise MlFoundryException(
                f"Failed to extract model files. Error: {e}"
            ) from e
        return codegen_dir

    def get_model_version(
        self,
        ml_repo: str,
        name: str,
        version: Union[str, int] = constants.LATEST_ARTIFACT_OR_MODEL_VERSION,
    ) -> Optional[ModelVersion]:
        """
        Get the model version to download contents or load it in memory

        Args:
            ml_repo (str): ML Repo to which model is logged
            name (str): Model Name
            version (str | int): Model Version to fetch (default is the latest version)

        Returns:
           ModelVersion: The ModelVersion instance of the model.

        Examples:

            ### Sklearn

            ```python
            # See `truefoundry.ml.mlfoundry_api.MlFoundry.log_model` examples to understand model logging
            import tempfile
            import joblib
            from truefoundry.ml import get_client

            client = get_client()
            model_version = client.get_model_version(
                ml_repo="my-classification-project",
                name="my-sklearn-model",
                version=1
            )

            # Download the model to disk
            temp = tempfile.TemporaryDirectory()
            download_info = model_version.download(path=temp.name)
            print(download_info.model_dir, download_info.model_filename)

            # Deserialize and Load
            model = joblib.load(
                os.path.join(download_info.model_dir, download_info.model_filename)
            )
            ```

            ### Huggingface Transformers

            ```python
            # See `truefoundry.ml.mlfoundry_api.MlFoundry.log_model` examples to understand model logging
            import torch
            from transformers import pipeline

            from truefoundry.ml import get_client

            client = get_client()
            model_version = client.get_model_version(
                ml_repo="my-llm-project",
                name="my-transformers-model",
                version=1
            )

            # Download the model to disk
            temp = tempfile.TemporaryDirectory()
            download_info = model_version.download(path=temp.name)
            print(download_info.model_dir)

            # Deserialize and Load
            pln = pipeline("text-generation", model=download_info.model_dir, torch_dtype=torch.float16)
            ```
        """
        resolved_version = None
        if version != constants.LATEST_ARTIFACT_OR_MODEL_VERSION:
            resolved_version = _resolve_version(version=version)

        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)

        _model_version = self._mlfoundry_artifacts_api.get_model_version_by_name_get(
            experiment_id=int(ml_repo_id),
            model_name=name,
            version=resolved_version,
        )
        model_version = _model_version.model_version
        _model = self._mlfoundry_artifacts_api.get_model_get(id=model_version.model_id)
        model = _model.model

        return ModelVersion(
            model_version=model_version,
            model=model,
        )

    def get_model_version_by_fqn(self, fqn: str) -> ModelVersion:
        """
        Get the model version to download contents or load it in memory

        Args:
            fqn (str): Fully qualified name of the model version.

        Returns:
            ModelVersion: The ModelVersion instance of the model.

        Examples:

            ### Sklearn

            ```python
            # See `truefoundry.ml.mlfoundry_api.MlFoundry.log_model` examples to understand model logging
            import tempfile
            import joblib
            from truefoundry.ml import get_client

            client = get_client()
            model_version = client.get_model_version_by_fqn(
                fqn="model:truefoundry/my-classification-project/my-sklearn-model:1"
            )

            # Download the model to disk
            temp = tempfile.TemporaryDirectory()
            download_info = model_version.download(path=temp.name)
            print(download_info.model_dir, download_info.model_filename)

            # Deserialize and Load
            model = joblib.load(
                os.path.join(download_info.model_dir, download_info.model_filename)
            )
            ```

            ### Huggingface Transformers

            ```python
            # See `truefoundry.ml.mlfoundry_api.MlFoundry.log_model` examples to understand model logging
            import torch
            from transformers import pipeline

            from truefoundry.ml import get_client

            client = get_client()
            model_version = client.get_model_version_by_fqn(
                fqn="model:truefoundry/my-llm-project/my-transformers-model:1"
            )
            # Download the model to disk
            temp = tempfile.TemporaryDirectory()
            download_info = model_version.download(path=temp.name)
            print(download_info.model_dir)

            # Deserialize and Load
            pln = pipeline("text-generation", model=download_info.model_dir, torch_dtype=torch.float16)
            ```
        """
        return ModelVersion.from_fqn(fqn=fqn)

    def list_model_versions(self, ml_repo: str, name: str) -> Iterator[ModelVersion]:
        """
        Get all the version of a model to download contents or load them in memory

        Args:
            ml_repo (str): Repository in which the model is stored.
            name (str): Name of the model whose version is required

        Returns:
            Iterator[ModelVersion]: An iterator that yields non deleted model versions
                of a model under a given ml_repo  sorted reverse by the version number

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            model_versions = client.list_model_version(ml_repo="my-repo", name="svm")

            for model_version in model_versions:
                print(model_version)
            ```
        """
        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        try:
            _model = self._mlfoundry_artifacts_api.get_model_by_name_get(
                experiment_id=int(ml_repo_id), name=name
            )
        except NotFoundException as e:
            err_msg = (
                f"Model Does Not Exist for ml_repo={ml_repo}, name={name}. Error: {e}"
            )
            raise MlFoundryException(err_msg) from e
        model = _model.model
        return self._list_model_versions_by_id(model=model)

    def list_model_versions_by_fqn(self, model_fqn: str) -> Iterator[ModelVersion]:
        """
        List versions for a given model

        Args:
            model_fqn: FQN of the Model to list versions for.
                A model_fqn looks like `model:{org}/{user}/{project}/{artifact_name}`
                or `model:{user}/{project}/{artifact_name}`

        Returns:
            Iterator[ModelVersion]: An iterator that yields non deleted model versions
                under the given model_fqn sorted reverse by the version number

        Yields:
            ModelVersion: An instance of `truefoundry.ml.ModelVersion`

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            model_fqn = "model:org/my-project/my-model"
            for mv in client.list_model_versions(model_fqn=model_fqn):
                print(mv.name, mv.version, mv.description)
            ```
        """
        _model = self._mlfoundry_artifacts_api.get_model_by_fqn_get(fqn=model_fqn)
        model = _model.model
        return self._list_model_versions_by_id(model=model)

    def _list_model_versions_by_id(
        self,
        model_id: Optional[uuid.UUID] = None,
        model: Optional[ModelDto] = None,
    ) -> Iterator[ModelVersion]:
        if model and not model_id:
            model_id = model.id
        elif not model and model_id:
            _model = self._mlfoundry_artifacts_api.get_model_get(id=str(model_id))
            model = _model.model
        else:
            raise MlFoundryException(
                "Exactly one of model_id or model should be passed"
            )

        max_results, page_token, done = 10, None, False
        while not done:
            _model_versions = self._mlfoundry_artifacts_api.list_model_versions_post(
                list_model_versions_request_dto=ListModelVersionsRequestDto(
                    model_id=str(model_id),
                    max_results=max_results,
                    page_token=page_token,
                )
            )
            model_versions = _model_versions.model_versions
            page_token = _model_versions.next_page_token
            for model_version in model_versions:
                yield ModelVersion(model_version=model_version, model=model)
            if not model_versions or not page_token:
                done = True

    def get_artifact_version(
        self,
        ml_repo: str,
        name: str,
        artifact_type: Optional[ArtifactType] = ArtifactType.ARTIFACT,
        version: Union[str, int] = constants.LATEST_ARTIFACT_OR_MODEL_VERSION,
    ) -> Optional[ArtifactVersion]:
        """
        Get the model version to download contents or load it in memory

        Args:
            ml_repo (str): ML Repo to which artifact is logged
            name (str): Artifact Name
            artifact_type (str): The type of artifact to fetch (acceptable values: "artifact", "model", "plot", "image")
            version (str | int): Artifact Version to fetch (default is the latest version)

        Returns:
            ArtifactVersion : An ArtifactVersion instance of the artifact

        Examples:

            ```python
            import tempfile
            from truefoundry.ml import get_client

            client = get_client()
            artifact_version = client.get_artifact_version(ml_repo="ml-repo-name", name="artifact-name", version=1)

            # download the artifact to disk
            temp = tempfile.TemporaryDirectory()
            download_path = artifact_version.download(path=temp.name)
            print(download_path)
            ```
        """
        resolved_version = None
        if version != constants.LATEST_ARTIFACT_OR_MODEL_VERSION:
            resolved_version = _resolve_version(version=version)

        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)

        _artifact_version = (
            self._mlfoundry_artifacts_api.get_artifact_version_by_name_get(
                experiment_id=int(ml_repo_id),
                artifact_name=name,
                artifact_type=artifact_type,
                version=resolved_version,
            )
        )
        artifact_version = _artifact_version.artifact_version
        _artifact = self._mlfoundry_artifacts_api.get_artifact_by_id_get(
            id=artifact_version.artifact_id
        )
        artifact = _artifact.artifact

        return ArtifactVersion(
            artifact_version=artifact_version,
            artifact=artifact,
        )

    def get_artifact_version_by_fqn(self, fqn: str) -> ArtifactVersion:
        """
        Get the artifact version to download contents

        Args:
            fqn (str): Fully qualified name of the artifact version.

        Returns:
            ArtifactVersion : An ArtifactVersion instance of the artifact

        Examples:

            ```python
            import tempfile
            from truefoundry.ml import get_client

            client = get_client()
            artifact_version = client.get_artifact_version_by_fqn(
                fqn="artifact:truefoundry/my-classification-project/sklearn-artifact:1"
            )

            # download the artifact to disk
            temp = tempfile.TemporaryDirectory()
            download_path = artifact_version.download(path=temp.name)
            print(download_path)
            ```
        """
        return ArtifactVersion.from_fqn(fqn=fqn)

    def list_artifact_versions(
        self,
        ml_repo: str,
        name: str,
        artifact_type: Optional[ArtifactType] = ArtifactType.ARTIFACT,
    ) -> Iterator[ArtifactVersion]:
        """
        Get all the version of na artifact to download contents or load them in memory

        Args:
            ml_repo (str): Repository in which the model is stored.
            name (str): Name of the artifact whose version is required
            artifact_type (ArtifactType): Type of artifact you want for example model, image, etc.

        Returns:
            Iterator[ArtifactVersion]: An iterator that yields non deleted artifact-versions
                of an artifact under a given ml_repo  sorted reverse by the version number

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            artifact_versions = client.list_artifact_versions(ml_repo="my-repo", name="artifact-name")

            for artifact_version in artifact_versions:
                print(artifact_version)
            ```
        """
        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        _artifacts = self._mlfoundry_artifacts_api.list_artifacts_post(
            list_artifacts_request_dto=ListArtifactsRequestDto(
                experiment_id=ml_repo_id,
                name=name,
                artifact_types=[artifact_type] if artifact_type else None,
                max_results=1,
            )
        )
        artifacts = _artifacts.artifacts
        if not artifacts or len(artifacts) == 0:
            err_msg = f"Artifact Does Not Exist for ml_repo={ml_repo}, name={name}, type={artifact_type}"
            raise MlFoundryException(err_msg)
        return self._list_artifact_versions_by_id(artifact=artifacts[0])

    def list_artifact_versions_by_fqn(
        self, artifact_fqn: str
    ) -> Iterator[ArtifactVersion]:
        """
        List versions for a given artifact

        Args:
            artifact_fqn: FQN of the Artifact to list versions for.
                An artifact_fqn looks like `{artifact_type}:{org}/{user}/{project}/{artifact_name}`
                or `{artifact_type}:{user}/{project}/{artifact_name}`

                where artifact_type can be on of ("model", "image", "plot")

        Returns:
            Iterator[ArtifactVersion]: An iterator that yields non deleted artifact versions
                under the given artifact_fqn sorted reverse by the version number

        Yields:
            ArtifactVersion: An instance of `truefoundry.ml.ArtifactVersion`

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            artifact_fqn = "artifact:org/my-project/my-artifact"
            for av in client.list_artifact_versions(artifact_fqn=artifact_fqn):
                print(av.name, av.version, av.description)
            ```
        """

        _artifact = self._mlfoundry_artifacts_api.get_artifact_by_fqn_get(
            fqn=artifact_fqn
        )
        artifact = _artifact.artifact
        return self._list_artifact_versions_by_id(artifact=artifact)

    def _list_artifact_versions_by_id(
        self,
        artifact_id: Optional[uuid.UUID] = None,
        artifact: Optional[ArtifactDto] = None,
    ) -> Iterator[ArtifactVersion]:
        if artifact and not artifact_id:
            artifact_id = artifact.id
        elif not artifact and artifact_id:
            _artifact = self._mlfoundry_artifacts_api.get_artifact_by_id_get(
                id=str(artifact_id)
            )
            artifact = _artifact.artifact
        else:
            raise MlFoundryException(
                "Exactly one of artifact_id or artifact should be passed"
            )

        max_results, page_token, done = 10, None, False
        while not done:
            _artifact_versions = (
                self._mlfoundry_artifacts_api.list_artifact_versions_post(
                    list_artifact_versions_request_dto=ListArtifactVersionsRequestDto(
                        artifact_id=str(artifact_id),
                        max_results=max_results,
                        page_token=page_token,
                    )
                )
            )
            artifact_versions = _artifact_versions.artifact_versions
            page_token = _artifact_versions.next_page_token
            for artifact_version in artifact_versions:
                yield ArtifactVersion(
                    artifact_version=artifact_version, artifact=artifact
                )
            if not artifact_versions or not page_token:
                done = True

    def log_artifact(
        self,
        ml_repo: str,
        name: str,
        artifact_paths: List[
            Union[Tuple[str], Tuple[str, Optional[str]], ArtifactPath]
        ],
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        progress: Optional[bool] = None,
    ) -> Optional[ArtifactVersion]:
        """Logs an artifact for the current `ml_repo`.

        An `artifact` is a list of local files and directories.
        This function packs the mentioned files and directories in `artifact_paths`
        and uploads them to remote storage linked to the ml_repo

        Args:
            ml_repo (str): Name of the ML Repo to which an artifact is to be logged.
            name (str): Name of the Artifact. If an artifact with this name already exists under the current ml_repo,
                the logged artifact will be added as a new version under that `name`. If no artifact exist with
                the given `name`, the given artifact will be logged as version 1.
            artifact_paths (List[truefoundry.ml.ArtifactPath], optional): A list of pairs
                of (source path, destination path) to add files and folders
                to the artifact version contents. The first member of the pair should be a file or directory path
                and the second member should be the path inside the artifact contents to upload to.
            progress (bool): value to show progress bar, defaults to None.

                ```python

                from truefoundry.ml import get_client, ArtifactPath

                client = get_client()
                client.log_artifact(
                    ml_repo="sample-repo",
                    name="xyz",
                    artifact_paths=[
                        ArtifactPath("foo.txt", "foo/bar/foo.txt"),
                        ArtifactPath("tokenizer/", "foo/tokenizer/"),
                        ArtifactPath('bar.text'),
                        ('bar.txt', ),
                        ('foo.txt', 'a/foo.txt')
                    ]
                )
                ```

                would result in

                ```
                .
                └── foo/
                    ├── bar/
                    │   └── foo.txt
                    └── tokenizer/
                        └── # contents of tokenizer/ directory will be uploaded here
                ```
            description (Optional[str], optional): arbitrary text upto 1024 characters to store as description.
                This field can be updated at any time after logging. Defaults to `None`
            metadata (Optional[Dict[str, Any]], optional): arbitrary json serializable dictionary to store metadata.
                For example, you can use this to store metrics, params, notes.
                This field can be updated at any time after logging. Defaults to `None`

        Returns:
            truefoundry.ml.ArtifactVersion: an instance of `ArtifactVersion` that can be used to download the files,
            or update attributes like description, metadata.

        Examples:

            ```python
            import os
            from truefoundry.ml import get_client, ArtifactPath

            with open("artifact.txt", "w") as f:
                f.write("hello-world")

            client = get_client()
            ml_repo = "sample-repo"

            client.create_ml_repo(
                ml_repo=ml_repo,
                # This controls which bucket is used.
                # You can get this from Platform > Integrations > Copy FQN of any Blob Storage type integration.
                storage_integration_fqn="..."
            )
            client.log_artifact(
                ml_repo=ml_repo,
                name="hello-world-file",
                artifact_paths=[ArtifactPath('artifact.txt', 'a/b/')]
            )
            ```
        """
        if not artifact_paths:
            raise MlFoundryException(
                "artifact_paths cannot be empty, atleast one artifact_path must be passed"
            )
        artifact_version = _log_artifact_version(
            run=None,
            ml_repo=ml_repo,
            name=name,
            artifact_paths=artifact_paths,
            description=description,
            metadata=metadata,
            step=None,
            progress=progress,
        )
        logger.info(f"Logged artifact successfully with fqn {artifact_version.fqn!r}")
        return artifact_version

    def log_model(
        self,
        *,
        ml_repo: str,
        name: str,
        model_file_or_folder: Union[str, BlobStorageDirectory],
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        progress: Optional[bool] = None,
        framework: Optional[Union[str, ModelFramework, "ModelFrameworkType"]] = None,
        environment: Optional[ModelVersionEnvironment] = None,
    ) -> ModelVersion:
        """
        Serialize and log a versioned model under the current ml_repo. Each logged model generates a new version
        associated with the given `name` and linked to the current run. Multiple versions of the model can be
        logged as separate versions under the same `name`.

        Args:
            ml_repo (str): Name of the ML Repo to which an artifact is to be logged.
            name (str): Name of the model. If a model with this name already exists under the current ML Repo,
                the logged model will be added as a new version under that `name`. If no models exist with the given
                `name`, the given model will be logged as version 1.

            model_file_or_folder (Union[str, BlobStorageDirectory]):
                str:
                    Path to either a single file or a folder containing model files.
                    This folder is typically created using serialization methods from libraries or frameworks,
                    e.g., `joblib.dump`, `model.save_pretrained(...)`, `torch.save(...)`, or `model.save(...)`.
                BlobStorageDirectory:
                    uri (str): URI to the model file or folder in a storage integration associated with the specified ML Repo.
                        The model files or folder must reside within the same storage integration as the specified ML Repo.
                        Accepted URI formats include `s3://integration-bucket-name/prefix/path/to/model` or `gs://integration-bucket-name/prefix/path/to/model`.
                        If the URI points to a model in a different storage integration, an error will be raised indicating "Invalid source URI."

            framework (Optional[Union[ModelFramework, ModelFrameworkType]]): Framework used for model serialization.
                Supported frameworks values (ModelFrameworkType) can be imported from `from truefoundry.ml import *`.
                Supported frameworks can be found in `truefoundry.ml.enums.ModelFramework`.
                Can also be `None` if the framework is not known or not supported.
                **Deprecated**: Prefer `ModelFrameworkType` over `enums.ModelFramework`.

            description (Optional[str], optional): arbitrary text upto 1024 characters to store as description.
                This field can be updated at any time after logging. Defaults to `None`
            metadata (Optional[Dict[str, Any]], optional): arbitrary json serializable dictionary to store metadata.
                For example, you can use this to store metrics, params, notes.
                This field can be updated at any time after logging. Defaults to `None`
            progress (bool): value to show progress bar, defaults to None.

        Returns:
            truefoundry.ml.ModelVersion: an instance of `ModelVersion` that can be used to download the files,
                load the model, or update attributes like description, metadata, schema.

        Examples:

            ### Sklearn

            ```python
            from truefoundry.ml import get_client, SklearnFramework

            import joblib
            import numpy as np
            from sklearn.pipeline import make_pipeline
            from sklearn.preprocessing import StandardScaler
            from sklearn.svm import SVC

            X = np.array([[-1, -1], [-2, -1], [1, 1], [2, 1]])
            y = np.array([1, 1, 2, 2])
            clf = make_pipeline(StandardScaler(), SVC(gamma='auto'))
            clf.fit(X, y)
            joblib.dump(clf, "sklearn-pipeline.joblib")

            client = get_client()
            client.create_ml_repo(  # This is only required once
                ml_repo="my-classification-project",
                # This controls which bucket is used.
                # You can get this from Platform > Integrations > Copy FQN of any Blob Storage type integration.
                storage_integration_fqn="..."
            )
            model_version = client.log_model(
                ml_repo="my-classification-project",
                name="my-sklearn-model",
                model_file_or_folder="sklearn-pipeline.joblib",
                framework=SklearnFramework(),
                metadata={"accuracy": 0.99, "f1": 0.80},
                step=1,  # step number, useful when using iterative algorithms like SGD
            )
            print(model_version.fqn)
            ```

            ### Huggingface Transformers

            ```python
            from truefoundry.ml import get_client, TransformersFramework, LibraryName

            import torch
            from transformers import AutoTokenizer, AutoConfig, pipeline, AutoModelForCausalLM
            pln = pipeline(
                "text-generation",
                model_file_or_folder="EleutherAI/pythia-70m",
                tokenizer="EleutherAI/pythia-70m",
                torch_dtype=torch.float16
            )
            pln.model.save_pretrained("my-transformers-model")
            pln.tokenizer.save_pretrained("my-transformers-model")

            client = get_client()
            client.create_ml_repo(  # This is only required once
                ml_repo="my-llm-project",
                # This controls which bucket is used.
                # You can get this from Integrations > Blob Storage. `None` picks the default
                storage_integration_fqn=None
            )
            model_version = client.log_model(
                ml_repo="my-llm-project",
                name="my-transformers-model",
                model_file_or_folder="my-transformers-model/",
                framework=TransformersFramework(library_name=LibraryName.TRANSFORMERS, pipeline_tag='text-generation')
            )
            print(model_version.fqn)
            ```

        """
        model_version = _log_model_version(
            run=None,
            ml_repo=ml_repo,
            name=name,
            model_file_or_folder=model_file_or_folder,
            description=description,
            metadata=metadata,
            step=None,
            progress=progress,
            framework=framework,
            environment=environment,
        )
        logger.info(f"Logged model successfully with fqn {model_version.fqn!r}")
        return model_version

    # Datasets API
    def create_data_directory(
        self,
        ml_repo: str,
        name: str,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> DataDirectory:
        """
        Create DataDirectory to Upload the files

        Args:
            ml_repo (str): Name of the ML Repo in which you want to create data_directory
            name (str): Name of the DataDirectory to be created.
            description (str): Description for the DataDirectory.
            metadata (Dict <str>: Any): Metadata about the data_directory in Dictionary form.

        Returns:
            DataDirectory : An instance of class DataDirectory

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            data_directory = client.create_data_directory(name="<data_directory-name>", ml_repo="<repo-name>")
            print(data_directory.fqn)
            ```
        """
        if name == "" or not isinstance(name, str):
            raise MlFoundryException(
                f"DataDirectory name must be string type and not empty. "
                f"Got {type(name)} type with value {name}"
            )

        if ml_repo == "" or not isinstance(ml_repo, str):
            raise MlFoundryException(
                f"ML repo must be string type and not empty. "
                f"Got {type(ml_repo)} type with value {ml_repo}"
            )

        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        # TODO: Add get_data_directory_by_name on server
        _datasets = self._mlfoundry_artifacts_api.list_datasets_post(
            list_datasets_request_dto=ListDatasetsRequestDto(
                experiment_id=ml_repo_id, name=name, max_results=1
            )
        )
        datasets = _datasets.datasets
        if datasets is not None and len(datasets) > 0:
            logger.warning(
                f"Data Directory with the name {name} already exists in ML Repo {ml_repo}, "
                f"returning the original instance of DataDirectory instead"
            )
            return DataDirectory(dataset=datasets[0])

        _dataset = self._mlfoundry_artifacts_api.create_dataset_post(
            create_dataset_request_dto=CreateDatasetRequestDto(
                name=name,
                experiment_id=ml_repo_id,
                description=description,
                dataset_metadata=metadata,
            )
        )
        dataset = _dataset.dataset
        return DataDirectory(dataset=dataset)

    def get_data_directory_by_fqn(
        self,
        fqn: str,
    ) -> DataDirectory:
        """
        Get the DataDirectory by DataDirectory FQN

        Args:
            fqn (str): Fully qualified name of the artifact version.

        Returns:
            DataDirectory : An instance of class DataDirectory

        Examples:

            ```python
            from truefoundry.ml import get_client, DataDirectoryPath

            client = get_client()
            data_directory = client.get_data_directory_by_fqn(fqn="<data-dir-fqn>")
            with open("artifact.txt", "w") as f:
                f.write("hello-world")

            data_directory.add_files(
                artifact_paths=[DataDirectoryPath('artifact.txt', 'a/b/')]
            )
            # print the path of files and folder in the data_directory
            for file in data_directory.list_files():
                print(file.path)
            ```
        """

        _dataset = self._mlfoundry_artifacts_api.get_dataset_by_fqn_get(fqn=fqn)
        dataset = _dataset.dataset
        return DataDirectory(dataset)

    def get_data_directory(
        self,
        ml_repo: str,
        name: str,
    ) -> DataDirectory:
        """Get an existing `data_directory` by `name`.
        Args:
            ml_repo (str): name of the ML Repo the data-directory is part of.
            name (str): the name of the data-directory
        Returns:
            DataDirectory: An instance of class DataDirectory
        Examples:
            ```python
            from truefoundry.ml import get_client
            client = get_client()
            data_directory = client.get_data_directory(ml_repo='my-repo', name="<data-directory-name>")
            with open("artifact.txt", "w") as f:
                f.write("hello-world")
            data_directory.add_files(
                artifact_paths=[DataDirectoryPath('artifact.txt', 'a/b/')]
            )
            # print the path of files and folder in the data_directory
            for file in data_directory.list_files():
                print(file.path)
            ```
        """
        if ml_repo == "" or not isinstance(ml_repo, str):
            raise MlFoundryException(
                f"ML repo must be string type and not empty. "
                f"Got {type(ml_repo)} type with value {ml_repo}"
            )
        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        _datasets = self._mlfoundry_artifacts_api.list_datasets_post(
            list_datasets_request_dto=ListDatasetsRequestDto(
                experiment_id=ml_repo_id,
                name=name,
                max_results=1,
            ),
        )
        datasets = _datasets.datasets
        if not datasets or len(datasets) == 0:
            raise MlFoundryException(
                f"No data directory found with name {name} under ML Repo {ml_repo}"
            )

        return DataDirectory(dataset=datasets[0])

    def list_data_directories(
        self,
        ml_repo: str,
    ) -> Iterator[DataDirectory]:
        """
        Get the list of DataDirectory in a ml_repo

        Args:
            ml_repo (str): Name of the ML Repository

        Returns:
            DataDirectory : An instance of class DataDirectory

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            data_directories = client.list_data_directories(ml_repo="<ml-repo-nam>")

            for data_directory in data_directories:
                print(data_directory.name)
            ```
        """
        if ml_repo == "" or not isinstance(ml_repo, str):
            raise MlFoundryException(
                f"ML repo must be string type and not empty. "
                f"Got {type(ml_repo)} type with value {ml_repo}"
            )
        ml_repo_id = self._get_ml_repo_id(ml_repo=ml_repo)
        max_results, page_token, done = 10, None, False
        while not done:
            _datasets = self._mlfoundry_artifacts_api.list_datasets_post(
                list_datasets_request_dto=ListDatasetsRequestDto(
                    experiment_id=ml_repo_id,
                    max_results=max_results,
                    page_token=page_token,
                )
            )
            datasets: List[DatasetDto] = _datasets.datasets or []
            page_token = _datasets.next_page_token
            for dataset in datasets:
                yield DataDirectory(dataset=dataset)
            if not datasets or not page_token:
                done = True


def get_client() -> MlFoundry:
    """Initializes and returns the mlfoundry client.


    Returns:
        MlFoundry: Instance of `MlFoundry` class which represents a `run`.

    Examples:

        ### Get client
        ```python
        from truefoundry.ml import get_client

        client = get_client()
        ```
    """
    session = MLFoundrySession.new()
    return MlFoundry(session=session)
