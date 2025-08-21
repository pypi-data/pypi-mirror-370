import functools
import os
import platform
import re
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)
from urllib.parse import urljoin, urlsplit

from truefoundry import client, version
from truefoundry.ml import constants
from truefoundry.ml._autogen.client import (  # type: ignore[attr-defined]
    ArtifactType,
    DeleteRunRequest,
    ListArtifactVersionsRequestDto,
    ListModelVersionsRequestDto,
    LogBatchRequestDto,
    MetricDto,
    MetricsApi,
    MlfoundryArtifactsApi,
    ModelVersionEnvironment,
    ParamDto,
    RunDataDto,
    RunDto,
    RunInfoDto,
    RunsApi,
    RunTagDto,
    UpdateRunRequestDto,
)
from truefoundry.ml.entities import Metric
from truefoundry.ml.enums import ModelFramework, RunStatus
from truefoundry.ml.exceptions import MlFoundryException
from truefoundry.ml.internal_namespace import NAMESPACE
from truefoundry.ml.log_types import Image, Plot
from truefoundry.ml.log_types.artifacts.artifact import (
    ArtifactPath,
    ArtifactVersion,
    BlobStorageDirectory,
)
from truefoundry.ml.log_types.artifacts.general_artifact import _log_artifact_version
from truefoundry.ml.log_types.artifacts.model import (
    ModelVersion,
    _log_model_version,
)
from truefoundry.ml.logger import logger
from truefoundry.ml.run_utils import ParamsType, flatten_dict, process_params
from truefoundry.ml.session import ACTIVE_RUNS, _get_api_client
from truefoundry.ml.validation_utils import (
    MAX_ENTITY_KEY_LENGTH,
    MAX_METRICS_PER_BATCH,
    MAX_PARAMS_TAGS_PER_BATCH,
    _validate_batch_log_data,
)

if TYPE_CHECKING:
    import matplotlib
    import plotly

    from truefoundry.ml import ModelFrameworkType


def _ensure_not_deleted(method):
    @functools.wraps(method)
    def _check_deleted_or_not(self: "MlFoundryRun", *args, **kwargs):
        if self._deleted:
            raise MlFoundryException("Run was deleted, cannot access a deleted Run")
        else:
            return method(self, *args, **kwargs)

    return _check_deleted_or_not


class MlFoundryRun:
    """MlFoundryRun."""

    VALID_PARAM_AND_METRIC_NAMES = re.compile(r"^[A-Za-z0-9_\-\. /]+$")

    def __init__(
        self,
        experiment_id: str,
        run_id: str,
        auto_end: bool = False,
        **kwargs,
    ):
        """__init__.

        Args:
            experiment_id (str): experiment_id
            run_id (str): run_id
            auto_end (bool): If to end the run at garbage collection or process end (atexit)
        """
        self._experiment_id = str(experiment_id)
        self._run_id = run_id
        self._auto_end = auto_end
        self._run_info: Optional[RunInfoDto] = None
        self._run_data: Optional[RunDataDto] = None
        self._deleted = False
        self._terminate_called = False
        if self._auto_end:
            ACTIVE_RUNS.add_run(self)

        self._api_client = _get_api_client()
        self._runs_api = RunsApi(api_client=self._api_client)
        self._metrics_api = MetricsApi(api_client=self._api_client)
        self._mlfoundry_artifacts_api = MlfoundryArtifactsApi(
            api_client=self._api_client
        )

    @classmethod
    def _from_dto(cls, run_dto: RunDto) -> "MlFoundryRun":
        """classmethod to get MLfoundry run from dto instance"""
        run = cls(run_dto.info.experiment_id, run_dto.info.run_id)
        run._run_info = run_dto.info
        run._run_data = run_dto.data
        return run

    def _get_run_info(self) -> RunInfoDto:
        if self._run_info is not None:
            return self._run_info

        _run = self._runs_api.get_run_get(run_id=self.run_id)
        self._run_info = _run.run.info
        return self._run_info

    @property
    @_ensure_not_deleted
    def run_id(self) -> str:
        """Get run_id for the current `run`"""
        return self._run_id

    @property
    @_ensure_not_deleted
    def run_name(self) -> str:
        """Get run_name for the current `run`"""
        run_info = self._get_run_info()
        return run_info.name

    @property
    @_ensure_not_deleted
    def fqn(self) -> str:
        """Get fqn for the current `run`"""
        run_info = self._get_run_info()
        return run_info.fqn

    @property
    @_ensure_not_deleted
    def status(self) -> RunStatus:
        """Get status for the current `run`"""
        _run = self._runs_api.get_run_get(run_id=self.run_id)
        assert _run.run.info.status is not None
        return RunStatus(_run.run.info.status)

    @property
    @_ensure_not_deleted
    def ml_repo(self) -> str:
        """Get ml_repo name of which the current `run` is part of"""
        _experiment = client.ml_repos.get(id=self._experiment_id)
        return _experiment.data.manifest.name

    @property
    @_ensure_not_deleted
    def auto_end(self) -> bool:
        """Tells whether automatic end for `run` is True or False"""
        return self._auto_end

    @_ensure_not_deleted
    def __repr__(self) -> str:
        return f"<{type(self).__name__} at 0x{id(self):x}: run={self.fqn!r}>"

    @_ensure_not_deleted
    def __enter__(self):
        return self

    def _terminate_run_if_running(self, termination_status: RunStatus):
        """_terminate_run_if_running.

        Args:
            termination_status (RunStatus): termination_status
        """
        if self._terminate_called:
            return

        # Prevent double execution for termination
        self._terminate_called = True
        ACTIVE_RUNS.remove_run(self)

        current_status = self.status
        try:
            # we do not need to set any termination status unless the run was in RUNNING state
            if current_status != RunStatus.RUNNING:
                return
            logger.info("Setting run status of %r to %r", self.fqn, termination_status)
            _run_update = self._runs_api.update_run_post(
                update_run_request_dto=UpdateRunRequestDto(
                    run_id=self.run_id,
                    status=termination_status.value,
                    end_time=int(time.time() * 1000),
                )
            )
            self._run_info = _run_update.run_info
        except Exception as e:
            logger.warning(
                f"failed to set termination status {termination_status} due to {e}"
            )
        logger.info(f"Finished run: {self.fqn!r}, Dashboard: {self.dashboard_link}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        status = RunStatus.FINISHED if exc_type is None else RunStatus.FAILED
        self._terminate_run_if_running(status)

    def __del__(self):
        if self._auto_end:
            self._terminate_run_if_running(RunStatus.FINISHED)

    @property
    @_ensure_not_deleted
    def dashboard_link(self) -> str:
        """Get Mlfoundry dashboard link for a `run`"""
        tfy_host = "{uri.scheme}://{uri.netloc}/".format(
            uri=urlsplit(self._api_client.tfy_host)
        )
        return urljoin(tfy_host, f"mlfoundry/{self._experiment_id}/run/{self.run_id}/")

    @_ensure_not_deleted
    def end(self, status: RunStatus = RunStatus.FINISHED):
        """End a `run`.

        This function marks the run as `FINISHED`.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            run = client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel"
            )
            # ...
            # Model training code
            # ...
            run.end()
            ```

            In case the run was created using the context manager approach,
            We do not need to call this function.

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
        """
        self._terminate_run_if_running(status)

    @_ensure_not_deleted
    def delete(self) -> None:
        """
        This function permanently delete the run

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            client.create_ml_repo('iris-learning')
            run = client.create_run(ml_repo="iris-learning", run_name="svm-model1")
            run.log_params({"learning_rate": 0.001})
            run.log_metrics({"accuracy": 0.7, "loss": 0.6})

            run.delete()
            ```

            In case we try to call or access any other function of that run after deleting
            then it will through MlfoundryException

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            client.create_ml_repo('iris-learning')
            run = client.create_run(ml_repo="iris-learning", run_name="svm-model1")
            run.log_params({"learning_rate": 0.001})
            run.log_metrics({"accuracy": 0.7, "loss": 0.6})

            run.delete()
            run.log_params({"learning_rate": 0.001})  # raises MlfoundryException
            ```
        """
        name = self.run_name
        try:
            self._runs_api.hard_delete_run_post(
                delete_run_request=DeleteRunRequest(run_id=self.run_id)
            )
            logger.info(f"Run {name} was deleted successfully")
            ACTIVE_RUNS.remove_run(self)
            self._deleted = True
            self._auto_end = False
        except Exception as ex:
            logger.warning(f"Failed to delete the run {name} because of {ex}")
            raise

    @_ensure_not_deleted
    def list_artifact_versions(
        self,
        artifact_type: Optional[ArtifactType] = ArtifactType.ARTIFACT,
    ) -> Iterator[ArtifactVersion]:
        """
        Get all the version of an artifact from a particular run to download contents or load them in memory

        Args:
            artifact_type: Type of the artifact you want

        Returns:
            Iterator[ArtifactVersion]: An iterator that yields non deleted artifact-versions
                of an artifact under a given run  sorted reverse by the version number

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            run = client.create_run(ml_repo="iris-learning", run_name="svm-model1")
            artifact_versions = run.list_artifact_versions()

            for artifact_version in artifact_versions:
                print(artifact_version)

            run.end()
            ```
        """
        done, page_token, max_results = False, None, 25
        while not done:
            _artifact_versions = (
                self._mlfoundry_artifacts_api.list_artifact_versions_post(
                    list_artifact_versions_request_dto=ListArtifactVersionsRequestDto(
                        run_ids=[self.run_id],
                        artifact_types=[artifact_type] if artifact_type else None,
                        max_results=max_results,
                        page_token=page_token,
                    )
                )
            )
            artifact_versions = _artifact_versions.artifact_versions
            page_token = _artifact_versions.next_page_token
            for artifact_version in artifact_versions:
                yield ArtifactVersion.from_fqn(artifact_version.fqn)
            if not artifact_versions or page_token is None:
                done = True

    @_ensure_not_deleted
    def list_model_versions(
        self,
    ) -> Iterator[ModelVersion]:
        """
        Get all the version of a models from a particular run to download contents or load them in memory

        Returns:
            Iterator[ModelVersion]: An iterator that yields non deleted model-versions
                under a given run  sorted reverse by the version number

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            run = client.get_run(run_id="<your-run-id>")
            model_versions = run.list_model_versions()

            for model_version in model_versions:
                print(model_version)

            run.end()
            ```
        """
        done, page_token, max_results = False, None, 25
        while not done:
            _model_versions = self._mlfoundry_artifacts_api.list_model_versions_post(
                list_model_versions_request_dto=ListModelVersionsRequestDto(
                    run_ids=[self.run_id],
                    max_results=max_results,
                    page_token=page_token,
                )
            )
            model_versions = _model_versions.model_versions
            page_token = _model_versions.next_page_token
            for model_version in model_versions:
                yield ModelVersion.from_fqn(fqn=model_version.fqn)
            if not model_versions or page_token is None:
                done = True

    def _add_git_info(self, root_path: Optional[str] = None):
        """_add_git_info.

        Args:
            root_path (Optional[str]): root_path
        """
        root_path = root_path or os.getcwd()
        try:
            from truefoundry.ml.git_info import GitInfo

            git_info = GitInfo(root_path)
            tags = [
                RunTagDto(
                    key=constants.GIT_COMMIT_TAG_NAME,
                    value=git_info.current_commit_sha,
                ),
                RunTagDto(
                    key=constants.GIT_BRANCH_TAG_NAME,
                    value=git_info.current_branch_name,
                ),
                RunTagDto(
                    key=constants.GIT_DIRTY_TAG_NAME, value=str(git_info.is_dirty)
                ),
            ]
            remote_url = git_info.remote_url
            if remote_url is not None:
                tags.append(
                    RunTagDto(key=constants.GIT_REMOTE_URL_NAME, value=remote_url)
                )
            _validate_batch_log_data(metrics=[], params=[], tags=tags)
            self._runs_api.log_run_batch_post(
                log_batch_request_dto=LogBatchRequestDto(run_id=self.run_id, tags=tags)
            )
        except Exception as ex:
            # no-blocking
            logger.warning(f"failed to log git info because {ex}")

    def _add_python_truefoundry_version(self):
        python_version = platform.python_version()
        truefoundry_version = version.__version__
        tags = [
            RunTagDto(
                key=constants.PYTHON_VERSION_TAG_NAME,
                value=python_version,
            ),
        ]

        if truefoundry_version:
            tags.append(
                RunTagDto(
                    key=constants.MLFOUNDRY_VERSION_TAG_NAME,
                    value=truefoundry_version,
                )
            )
            tags.append(
                RunTagDto(
                    key=constants.TRUEFOUNDRY_VERSION_TAG_NAME,
                    value=truefoundry_version,
                )
            )
        else:
            logger.warning("Failed to get MLFoundry version.")
        _validate_batch_log_data(metrics=[], params=[], tags=tags)
        self._runs_api.log_run_batch_post(
            log_batch_request_dto=LogBatchRequestDto(run_id=self.run_id, tags=tags)
        )

    @_ensure_not_deleted
    def log_artifact(
        self,
        name: str,
        artifact_paths: List[
            Union[Tuple[str], Tuple[str, Optional[str]], ArtifactPath]
        ],
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        step: Optional[int] = 0,
        progress: Optional[bool] = None,
    ) -> ArtifactVersion:
        """Logs an artifact for the current ML Repo.

        An `artifact` is a list of local files and directories.
        This function packs the mentioned files and directories in `artifact_paths`
        and uploads them to remote storage linked to the experiment

        Args:
            name (str): Name of the Artifact. If an artifact with this name already exists under the current ML Repo,
                the logged artifact will be added as a new version under that `name`.
                If no artifact exist with the given `name`, the given artifact will be logged as version 1.
            artifact_paths (List[truefoundry.ml.ArtifactPath], optional): A list of pairs
                of (source path, destination path) to add files and folders
                to the artifact version contents. The first member of the pair should be a file or directory path
                and the second member should be the path inside the artifact contents to upload to.

                ```python
                from truefoundry.ml import ArtifactPath

                ...
                run.log_artifact(
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
            step (int): step/iteration at which the vesion is being logged, defaults to 0.
            progress (bool): value to show progress bar, defaults to None.

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
            run = client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel"
            )

            run.log_artifact(
                name="hello-world-file",
                artifact_paths=[ArtifactPath('artifact.txt', 'a/b/')]
            )

            run.end()
            ```
        """
        if not artifact_paths:
            raise MlFoundryException(
                "artifact_paths cannot be empty, atleast one artifact_path must be passed"
            )

        return _log_artifact_version(
            run=self,
            name=name,
            artifact_paths=artifact_paths,
            description=description,
            metadata=metadata,
            step=step,
            progress=progress,
        )

    @_ensure_not_deleted
    def log_metrics(self, metric_dict: Dict[str, Union[int, float]], step: int = 0):
        """Log metrics for the current `run`.

        A metric is defined by a metric name (such as "training-loss") and a
        floating point or integral value (such as `1.2`). A metric is associated
        with a `step` which is the training iteration at which the metric was
        calculated.

        Args:
            metric_dict (Dict[str, Union[int, float]]): A metric name to metric value map.
                metric value should be either `float` or `int`. This should be
                a non-empty dictionary.
            step (int, optional): Training step/iteration at which the metrics
                present in `metric_dict` were calculated. If not passed, `0` is
                set as the `step`.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.log_metrics(metric_dict={"accuracy": 0.7, "loss": 0.6}, step=0)
            run.log_metrics(metric_dict={"accuracy": 0.8, "loss": 0.4}, step=1)

            run.end()
            ```
        """
        timestamp = int(time.time() * 1000)
        metrics = []
        for key in metric_dict.keys():
            if isinstance(metric_dict[key], str):
                logger.warning(
                    f"Cannot log metric with string value. Discarding metric {key}={metric_dict[key]}"
                )
                continue
            if not self.VALID_PARAM_AND_METRIC_NAMES.match(key):
                logger.warning(
                    f"Invalid metric name: {key}. Names may only contain alphanumerics, "
                    f"underscores (_), dashes (-), periods (.), spaces ( ), and slashes (/). "
                    f"Discarding metric {key}={metric_dict[key]}"
                )
                continue
            metrics.append(
                MetricDto(
                    key=key, value=metric_dict[key], timestamp=timestamp, step=step
                )
            )

        if len(metrics) == 0:
            logger.warning("Cannot log empty metrics dictionary")
            return

        try:
            for i in range(0, len(metrics), MAX_METRICS_PER_BATCH):
                metrics_batch = metrics[i : i + MAX_METRICS_PER_BATCH]

                _validate_batch_log_data(metrics=metrics_batch, params=[], tags=[])

                self._runs_api.log_run_batch_post(
                    log_batch_request_dto=LogBatchRequestDto(
                        run_id=self.run_id, metrics=metrics_batch, params=[], tags=[]
                    )
                )
        except Exception as e:
            raise MlFoundryException(str(e)) from e

        logger.info("Metrics logged successfully")

    @_ensure_not_deleted
    def log_params(self, param_dict: ParamsType, flatten_params: bool = False):
        """Logs parameters for the run.

        Parameters or Hyperparameters can be thought of as configurations for a run.
        For example, the type of kernel used in a SVM model is a parameter.
        A Parameter is defined by a name and a string value. Parameters are
        also immutable, we cannot overwrite parameter value for a parameter
        name.

        Args:
            param_dict (ParamsType): A parameter name to parameter value map.
                Parameter values are converted to `str`.
            flatten_params (bool): Flatten hierarchical dict, e.g. `{'a': {'b': 'c'}} -> {'a.b': 'c'}`.
                All the keys will be converted to `str`. Defaults to False

        Examples:

            ### Logging parameters using a `dict`.

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.log_params({"learning_rate": 0.01, "epochs": 10})

            run.end()
            ```

            ### Logging parameters using `argparse` Namespace object

            ```python
            import argparse
            from truefoundry.ml import get_client

            parser = argparse.ArgumentParser()
            parser.add_argument("-batch_size", type=int, required=True)
            args = parser.parse_args()

            client = get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.log_params(args)
            ```
        """
        try:
            param_dict = process_params(param_dict)
            param_dict = flatten_dict(param_dict) if flatten_params else param_dict

            params = []
            for param_key in param_dict.keys():
                if (
                    len(str(param_key)) > MAX_ENTITY_KEY_LENGTH
                    or len(str(param_dict[param_key])) > MAX_ENTITY_KEY_LENGTH
                ):
                    logger.warning(
                        f"MlFoundry can't log parameters with length greater than {MAX_ENTITY_KEY_LENGTH} characters. "
                        f"Discarding {param_key}:{param_dict[param_key]}."
                    )
                    continue
                if not self.VALID_PARAM_AND_METRIC_NAMES.match(param_key):
                    logger.warning(
                        f"Invalid param name: {param_key}. Names may only contain alphanumerics, "
                        f"underscores (_), dashes (-), periods (.), spaces ( ), and slashes (/). "
                        f"Discarding param {param_key}={param_dict[param_key]}"
                    )
                    continue
                params.append(ParamDto(key=param_key, value=str(param_dict[param_key])))

            if len(params) == 0:
                logger.warning("Cannot log empty params dictionary")

            for i in range(0, len(params), MAX_PARAMS_TAGS_PER_BATCH):
                params_batch = params[i : i + MAX_PARAMS_TAGS_PER_BATCH]

                _validate_batch_log_data(metrics=[], params=params_batch, tags=[])
                logger.debug("Logging parameters: %s", params_batch)

                self._runs_api.log_run_batch_post(
                    log_batch_request_dto=LogBatchRequestDto(
                        run_id=self.run_id, metrics=[], params=params_batch, tags=[]
                    )
                )
        except Exception as e:
            raise MlFoundryException(str(e)) from e
        logger.info("Parameters logged successfully")

    @_ensure_not_deleted
    def set_tags(self, tags: Dict[str, str]):
        """Set tags for the current `run`.

        Tags are "labels" for a run. A tag is represented by a tag name and value.

        Args:
            tags (Dict[str, str]): A tag name to value map.
                Tag name cannot start with `mlf.`, `mlf.` prefix
                is reserved for truefoundry. Tag values will be converted
                to `str`.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.set_tags({"nlp.framework": "Spark NLP"})

            run.end()
            ```
        """
        tags = tags or {}
        try:
            NAMESPACE.validate_namespace_not_used(names=tags.keys())
            tags_arr = [
                RunTagDto(key=key, value=str(value)) for key, value in tags.items()
            ]
            for i in range(0, len(tags_arr), MAX_PARAMS_TAGS_PER_BATCH):
                tags_batch = tags_arr[i : i + MAX_PARAMS_TAGS_PER_BATCH]

                _validate_batch_log_data(metrics=[], params=[], tags=tags_batch)
                self._runs_api.log_run_batch_post(
                    log_batch_request_dto=LogBatchRequestDto(
                        run_id=self.run_id, metrics=[], params=[], tags=tags_batch
                    )
                )
        except Exception as e:
            raise MlFoundryException(str(e)) from e
        logger.info("Tags set successfully")

    @_ensure_not_deleted
    def get_tags(self, no_cache=False) -> Dict[str, str]:
        """Returns all the tags set for the current `run`.

        Returns:
            Dict[str, str]: A dictionary containing tags. The keys in the dictionary
                are tag names and the values are corresponding tag values.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.set_tags({"nlp.framework": "Spark NLP"})
            print(run.get_tags())

            run.end()
            ```
        """
        if no_cache or not self._run_data:
            _run = self._runs_api.get_run_get(run_id=self.run_id)
            self._run_data = _run.run.data
        assert self._run_data is not None
        tags = self._run_data.tags or []
        return {tag.key: tag.value for tag in tags}

    @_ensure_not_deleted
    def get_metrics(
        self, metric_names: Optional[Iterable[str]] = None
    ) -> Dict[str, List[Metric]]:
        """Get metrics logged for the current `run` grouped by metric name.

        Args:
            metric_names (Optional[Iterable[str]], optional): A list of metric names
                For which the logged metrics will be fetched. If not passed, then all
                metrics logged under the `run` is returned.

        Returns:
            Dict[str, List[Metric]]: A dictionary containing metric name to list of metrics
                map.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            run = client.create_run(
                ml_repo="my-classification-project", run_name="svm-with-rbf-kernel"
            )
            run.log_metrics(metric_dict={"accuracy": 0.7, "loss": 0.6}, step=0)
            run.log_metrics(metric_dict={"accuracy": 0.8, "loss": 0.4}, step=1)

            metrics = run.get_metrics()
            for metric_name, metric_history in metrics.items():
                print(f"logged metrics for metric {metric_name}:")
                for metric in metric_history:
                    print(f"value: {metric.value}")
                    print(f"step: {metric.step}")
                    print(f"timestamp_ms: {metric.timestamp}")
                    print("--")

            run.end()
            ```
        """
        _run = self._runs_api.get_run_get(run_id=self.run_id)
        assert _run.run.data is not None
        run_metrics = _run.run.data.metrics or []
        run_metric_names = {metric.key for metric in run_metrics}

        metric_names = (
            set(metric_names) if metric_names is not None else run_metric_names
        )

        unknown_metrics = metric_names - run_metric_names
        if len(unknown_metrics) > 0:
            logger.warning(f"{unknown_metrics} metrics not present in the run")
        metrics_dict: Dict[str, List[Metric]] = {
            metric_name: [] for metric_name in unknown_metrics
        }
        valid_metrics = metric_names - unknown_metrics
        for metric_name in valid_metrics:
            _metric_history = self._metrics_api.get_metric_history_get(
                run_id=self.run_id, metric_key=metric_name
            )
            metrics_dict[metric_name] = [
                Metric.from_dto(metric) for metric in _metric_history.metrics
            ]
        return metrics_dict

    @_ensure_not_deleted
    def get_params(self, no_cache=False) -> Dict[str, str]:
        """Get all the params logged for the current `run`.

        Returns:
            Dict[str, str]: A dictionary containing the parameters. The keys in the dictionary
                are parameter names and the values are corresponding parameter values.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            run.log_params({"learning_rate": 0.01, "epochs": 10})
            print(run.get_params())

            run.end()
            ```
        """
        if no_cache or not self._run_data:
            _run = self._runs_api.get_run_get(run_id=self.run_id)
            self._run_data = _run.run.data
        assert self._run_data is not None
        params = self._run_data.params or []
        return {param.key: param.value for param in params}

    @_ensure_not_deleted
    def log_model(
        self,
        *,
        name: str,
        model_file_or_folder: Union[str, BlobStorageDirectory],
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        step: int = 0,
        progress: Optional[bool] = None,
        framework: Optional[Union[str, ModelFramework, "ModelFrameworkType"]] = None,
        environment: Optional[ModelVersionEnvironment] = None,
    ) -> ModelVersion:
        # TODO (chiragjn): Document mapping of framework to list of valid model save kwargs
        # TODO (chiragjn): Add more examples
        """
        Serialize and log a versioned model under the current ML Repo. Each logged model generates a new version
            associated with the given `name` and linked to the current run. Multiple versions of the model can be
            logged as separate versions under the same `name`.

        Args:
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
            step (int): step/iteration at which the model is being logged, defaults to 0.
            progress (bool): value to show progress bar, defaults to None.

        Returns:
            truefoundry.ml.ModelVersion: an instance of `ModelVersion` that can be used to download the files,
                load the model, or update attributes like description, metadata, schema.

        Examples:

            ### Sklearn

            ```python
            from truefoundry.ml import get_client
            from truefoundry.ml.enums import ModelFramework

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
                # You can get this from Integrations > Blob Storage. `None` picks the default
                storage_integration_fqn=None
            )
            run = client.create_run(
                ml_repo="my-classification-project"
            )
            model_version = run.log_model(
                name="my-sklearn-model",
                model_file_or_folder="sklearn-pipeline.joblib",
                framework=ModelFramework.SKLEARN,
                metadata={"accuracy": 0.99, "f1": 0.80},
                step=1,  # step number, useful when using iterative algorithms like SGD
            )
            print(model_version.fqn)
            ```

            ### Huggingface Transformers

            ```python
            from truefoundry.ml import get_client
            from truefoundry.ml.enums import ModelFramework

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
            run = client.create_run(
                ml_repo="my-llm-project"
            )
            model_version = run.log_model(
                name="my-transformers-model",
                model_file_or_folder="my-transformers-model/",
                framework=ModelFramework.TRANSFORMERS
            )
            print(model_version.fqn)
            ```
        """

        model_version = _log_model_version(
            run=self,
            name=name,
            model_file_or_folder=model_file_or_folder,
            description=description,
            metadata=metadata,
            step=step,
            progress=progress,
            framework=framework,
            environment=environment,
        )
        logger.info(f"Logged model successfully with fqn {model_version.fqn!r}")
        return model_version

    @_ensure_not_deleted
    def log_images(self, images: Dict[str, Image], step: int = 0):
        """Log images under the current `run` at the given `step`.

        Use this function to log images for a `run`. `PIL` package is needed to log images.
        To install the `PIL` package, run `pip install pillow`.

        Args:
            images (Dict[str, "truefoundry.ml.Image"]): A map of string image key to instance of
                `truefoundry.ml.Image` class. The image key should only contain alphanumeric,
                hyphens(-) or underscores(_). For a single key and step pair, we can log only
                one image.
            step (int, optional): Training step/iteration for which the `images` should be
                logged. Default is `0`.

        Examples:

            ### Logging images from different sources

            ```python
            from truefoundry.ml import get_client, Image
            import numpy as np
            import PIL.Image

            client = get_client()
            run = client.create_run(
                ml_repo="my-classification-project",
            )

            imarray = np.random.randint(low=0, high=256, size=(100, 100, 3))
            im = PIL.Image.fromarray(imarray.astype("uint8")).convert("RGB")
            im.save("result_image.jpeg")

            images_to_log = {
                "logged-image-array": Image(data_or_path=imarray),
                "logged-pil-image": Image(data_or_path=im),
                "logged-image-from-path": Image(data_or_path="result_image.jpeg"),
            }

            run.log_images(images_to_log, step=1)
            run.end()
            ```
        """
        for key, image in images.items():
            if not isinstance(image, Image):
                raise MlFoundryException(
                    "image should be of type `truefoundry.ml.Image`"
                )
            image.save(run=self, key=key, step=step)

    @_ensure_not_deleted
    def log_plots(
        self,
        plots: Dict[  # type: ignore[valid-type]
            str,
            Union[
                "matplotlib.pyplot",
                "matplotlib.figure.Figure",
                "plotly.graph_objects.Figure",
                Plot,
            ],
        ],
        step: int = 0,
    ):
        """Log custom plots under the current `run` at the given `step`.

        Use this function to log custom matplotlib, plotly plots.

        Args:
            plots (Dict[str, "matplotlib.pyplot", "matplotlib.figure.Figure", "plotly.graph_objects.Figure", Plot]):
                A map of string plot key to the plot or figure object.
                The plot key should only contain alphanumeric, hyphens(-) or
                underscores(_). For a single key and step pair, we can log only
                one image.
            step (int, optional): Training step/iteration for which the `plots` should be
                logged. Default is `0`.


        Examples:

            ### Logging a plotly figure

            ```python
            from truefoundry.ml import get_client
            import plotly.express as px

            client = get_client()
            run = client.create_run(
                ml_repo="my-classification-project",
            )

            df = px.data.tips()
            fig = px.histogram(
                df,
                x="total_bill",
                y="tip",
                color="sex",
                marginal="rug",
                hover_data=df.columns,
            )

            plots_to_log = {
                "distribution-plot": fig,
            }

            run.log_plots(plots_to_log, step=1)
            run.end()
            ```


            ### Logging a matplotlib plt or figure

            ```python
            from truefoundry.ml import get_client
            from matplotlib import pyplot as plt
            import numpy as np

            client = get_client()
            run = client.create_run(
                ml_repo="my-classification-project",
            )

            t = np.arange(0.0, 5.0, 0.01)
            s = np.cos(2 * np.pi * t)
            (line,) = plt.plot(t, s, lw=2)

            plt.annotate(
                "local max",
                xy=(2, 1),
                xytext=(3, 1.5),
                arrowprops=dict(facecolor="black", shrink=0.05),
            )

            plt.ylim(-2, 2)

            plots_to_log = {"cos-plot": plt, "cos-plot-using-figure": plt.gcf()}

            run.log_plots(plots_to_log, step=1)
            run.end()
            ```
        """
        for key, plot in plots.items():
            plot = Plot(plot) if not isinstance(plot, Plot) else plot
            plot.save(run=self, key=key, step=step)
