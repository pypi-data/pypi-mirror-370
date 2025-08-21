import copy
import datetime
import json
import logging
import os.path
import tempfile
import uuid
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Optional, Union

from truefoundry import client
from truefoundry.common.warnings import TrueFoundryDeprecationWarning
from truefoundry.ml._autogen.client import (  # type: ignore[attr-defined]
    ArtifactType,
    CreateArtifactVersionRequestDto,
    DeleteArtifactVersionsRequestDto,
    ExternalBlobStorageSource,
    FinalizeArtifactVersionRequestDto,
    Framework,
    MlfoundryArtifactsApi,
    ModelDto,
    ModelManifest,
    ModelVersionDto,
    ModelVersionEnvironment,
    NotifyArtifactVersionFailureDto,
    TrueFoundryManagedSource,
    UpdateModelVersionRequestDto,
)
from truefoundry.ml._autogen.models import infer_signature as _infer_signature
from truefoundry.ml.artifact.truefoundry_artifact_repo import (
    ArtifactIdentifier,
    MlFoundryArtifactsRepository,
)
from truefoundry.ml.enums import ModelFramework
from truefoundry.ml.exceptions import MlFoundryException
from truefoundry.ml.log_types.artifacts.artifact import BlobStorageDirectory
from truefoundry.ml.log_types.artifacts.constants import (
    ARTIFACT_METADATA_TRUEFOUNDRY_KEY,
    INTERNAL_METADATA_PATH,
)
from truefoundry.ml.log_types.artifacts.utils import (
    _copy_additional_files,
    _get_src_dest_pairs,
    _validate_artifact_metadata,
    _validate_description,
    calculate_total_size,
    get_autogen_type,
    set_tfy_internal_metadata,
)
from truefoundry.ml.model_framework import (
    ModelFrameworkType,
    _ModelFramework,
    auto_update_environment_details,
    auto_update_model_framework_details,
)
from truefoundry.ml.session import _get_api_client
from truefoundry.pydantic_v1 import BaseModel, Extra, parse_obj_as

if TYPE_CHECKING:
    import numpy as np
    import pandas as pd

    from truefoundry.ml.mlfoundry_run import MlFoundryRun


logger = logging.getLogger(__name__)


# TODO: Support async download and upload
class ModelVersionInternalMetadata(BaseModel):
    class Config:
        extra = Extra.allow

    files_dir: str  # relative to root
    model_dir: str  # relative to `files_dir`
    model_is_null: bool = False
    framework: ModelFramework = ModelFramework.UNKNOWN
    transformers_pipeline_task: Optional[str] = None
    model_filename: Optional[str] = None
    mlfoundry_version: Optional[str] = None
    truefoundry_version: Optional[str] = None

    def dict(self, *args, **kwargs):
        dct = super().dict(*args, **kwargs)
        dct["framework"] = dct["framework"].value
        return dct


class ModelVersionDownloadInfo(BaseModel):
    download_dir: str
    model_dir: str
    model_framework: ModelFramework = ModelFramework.UNKNOWN
    model_filename: Optional[str] = None


class ModelVersion:
    def __init__(
        self,
        model_version: ModelVersionDto,
        model: ModelDto,
    ) -> None:
        self._api_client = _get_api_client()
        self._mlfoundry_artifacts_api = MlfoundryArtifactsApi(
            api_client=self._api_client
        )
        self._model_version = model_version
        self._model = model
        self._deleted = False
        self._description: str = ""
        self._metadata: Dict[str, Any] = {}
        self._environment: Optional[ModelVersionEnvironment] = None
        self._framework: Optional[ModelFrameworkType] = None
        self._version_alias: Optional[str] = None
        self._set_mutable_attrs()

    @classmethod
    def from_fqn(cls, fqn: str) -> "ModelVersion":
        """
        Get the version of a model to download contents or load them in memory

        Args:
            fqn (str): Fully qualified name of the model version.

        Returns:
            ModelVersion: An ModelVersion instance of the Model

        Examples:

            ```python
            from truefoundry.ml import get_client, ModelVersion

            client = get_client()
            model_version = ModelVersion.from_fqn(fqn="<your-model-fqn>")
            ```
        """
        api_client = _get_api_client()
        mlfoundry_artifacts_api = MlfoundryArtifactsApi(api_client=api_client)
        _model_version = mlfoundry_artifacts_api.get_model_version_by_fqn_get(fqn=fqn)
        model_version = _model_version.model_version
        _model = mlfoundry_artifacts_api.get_model_get(id=model_version.model_id)
        model = _model.model
        instance = cls(model_version=model_version, model=model)
        return instance

    def _ensure_not_deleted(self):
        if self._deleted:
            raise MlFoundryException(
                "Model Version was deleted, cannot perform updates on a deleted version"
            )

    def _set_mutable_attrs(self):
        if self._model_version.manifest:
            manifest = self._model_version.manifest
            self._description = manifest.description or ""
            self._metadata = copy.deepcopy(manifest.metadata)
            self._environment = copy.deepcopy(manifest.environment)
            self._framework = (
                parse_obj_as(
                    ModelFrameworkType, manifest.framework.actual_instance.to_dict()
                )
                if manifest.framework
                else None
            )
            self._version_alias = self._model_version.manifest.version_alias or None
        else:
            self._description = self._model_version.description or ""
            self._metadata = copy.deepcopy(self._model_version.artifact_metadata or {})
            self._environment = None
            self._framework = _ModelFramework.to_model_framework_type(
                self._model_version.model_framework
            )
            self._version_alias = None

    def _refetch_model_version(self, reset_mutable_attrs: bool = True):
        _model_version = self._mlfoundry_artifacts_api.get_model_version_get(
            id=self._model_version.id
        )
        self._model_version = _model_version.model_version
        if reset_mutable_attrs:
            self._set_mutable_attrs()

    def __repr__(self):
        return f"{self.__class__.__name__}(fqn={self.fqn!r})"

    def _get_artifacts_repo(self):
        return MlFoundryArtifactsRepository(
            artifact_identifier=ArtifactIdentifier(
                artifact_version_id=uuid.UUID(self._model_version.id)
            ),
            api_client=self._api_client,
        )

    @property
    def name(self) -> str:
        """Get the name of the model"""
        return self._model.name

    @property
    def model_fqn(self) -> str:
        """Get fqn of the model"""
        return self._model.fqn

    @property
    def version(self) -> int:
        """Get version information of the model"""
        return self._model_version.version

    @property
    def fqn(self) -> str:
        """Get fqn of the current model version"""
        return self._model_version.fqn

    @property
    def step(self) -> Optional[int]:
        """Get the step in which model was created"""
        if self._model_version.manifest:
            return self._model_version.manifest.step
        return self._model_version.step

    @property
    def description(self) -> str:
        """Get description of the model"""
        return self._description

    @description.setter
    def description(self, value: str):
        """set the description of the model"""
        _validate_description(value)
        self._description = value

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata for the current model"""
        return self._metadata

    @metadata.setter
    def metadata(self, value: Dict[str, Any]):
        """set the metadata for current model"""
        _validate_artifact_metadata(value)
        self._metadata = copy.deepcopy(value)

    @property
    def version_alias(self) -> Optional[str]:
        """
        Get version alias for the current model version
        """
        if not self._model_version.manifest:
            warnings.warn(
                message="This model version was created using an older serialization format. version alias does not exist",
                category=TrueFoundryDeprecationWarning,
                stacklevel=2,
            )
        return self._version_alias

    @version_alias.setter
    def version_alias(self, value: Optional[str]):
        """
        Set the version alias for current artifact version
        """
        if not self._model_version.manifest:
            warnings.warn(
                message="This model version was created using an older serialization format. version alias will not be updated",
                category=TrueFoundryDeprecationWarning,
                stacklevel=2,
            )
            return
        self._version_alias = value

    @property
    def environment(self) -> Optional[ModelVersionEnvironment]:
        """Get the environment details for the model"""
        if not self._model_version.manifest:
            warnings.warn(
                message="This model version was created using an older serialization format. environment does not exist, returning None",
                category=TrueFoundryDeprecationWarning,
                stacklevel=2,
            )
        return self._environment

    @environment.setter
    def environment(self, value: Optional[ModelVersionEnvironment]):
        """set the environment details for the model"""
        if not self._model_version.manifest:
            warnings.warn(
                message="This model version was created using an older serialization format. Environment will not be updated",
                category=TrueFoundryDeprecationWarning,
                stacklevel=2,
            )
            return
        self._environment = copy.deepcopy(value)

    @property
    def framework(self) -> Optional["ModelFrameworkType"]:
        """Get the framework of the model"""
        return self._framework

    @framework.setter
    def framework(
        self, value: Optional[Union[str, ModelFramework, "ModelFrameworkType"]]
    ):
        """Set the framework of the model"""
        if not self._model_version.manifest:
            warnings.warn(
                message="This model version was created using an older serialization format. Framework will not be updated",
                category=TrueFoundryDeprecationWarning,
                stacklevel=2,
            )
            return
        self._framework = _ModelFramework.to_model_framework_type(value)

    @property
    def created_at(self) -> Optional[datetime.datetime]:
        """Get the time at which model version was created"""
        return self._model_version.created_at

    @property
    def updated_at(self) -> Optional[datetime.datetime]:
        """Get the information about when the model version was updated"""
        return self._model_version.updated_at

    def raw_download(
        self,
        path: Optional[Union[str, Path]],
        overwrite: bool = False,
        progress: Optional[bool] = None,
    ) -> str:
        """
        Download a model file or directory to a local directory if applicable, and return a
        local path for it.

        Args:
            path (str): Absolute path of the local filesystem destination directory to which to
                        download the specified models. This directory must already exist.
                        If unspecified, the models will either be downloaded to a new
                        uniquely-named directory on the local filesystem.
            overwrite (bool): If True it will overwrite the file if it is already present in the download directory else
                              it will throw an error
            progress (bool): value to show progress bar, defaults to None.

        Returns:
            path:  Absolute path of the local filesystem location containing the desired models.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            model_version = client.get_model_version_by_fqn(fqn="<your-model-fqn>")
            model_version.raw_download(path="<your-desired-download-path>")
            ```
        """
        logger.info("Downloading model version contents, this might take a while ...")
        artifacts_repo = self._get_artifacts_repo()
        return artifacts_repo.download_artifacts(
            artifact_path="", dst_path=path, overwrite=overwrite, progress=progress
        )

    def _download(
        self,
        path: Optional[Union[str, Path]],
        overwrite: bool = False,
        progress: Optional[bool] = None,
    ) -> ModelVersionDownloadInfo:
        self._ensure_not_deleted()
        download_dir = self.raw_download(
            path=path, overwrite=overwrite, progress=progress
        )

        if self._model_version.manifest:
            _framework = self._model_version.manifest.framework
            model_framework = (
                ModelFramework(_framework.actual_instance.type)
                if _framework
                else ModelFramework.UNKNOWN
            )
            download_info = ModelVersionDownloadInfo(
                download_dir=download_dir,
                model_dir=download_dir,
                model_framework=model_framework,
                model_filename=None,
            )
            return download_info

        internal_metadata_path = os.path.join(download_dir, INTERNAL_METADATA_PATH)
        if not os.path.exists(internal_metadata_path):
            raise MlFoundryException(
                "Model version seems to be corrupted or in invalid format due to missing model metadata. "
                "You can still use .raw_download(path='/your/path/here') to download and inspect files."
            )
        with open(internal_metadata_path) as f:
            internal_metadata = ModelVersionInternalMetadata.parse_obj(json.load(f))
        download_info = ModelVersionDownloadInfo(
            download_dir=os.path.join(download_dir, internal_metadata.files_dir),
            model_dir=os.path.join(
                download_dir,
                internal_metadata.files_dir,
                internal_metadata.model_dir,
            ),
            model_framework=internal_metadata.framework,
            model_filename=internal_metadata.model_filename,
        )
        return download_info

    def download(
        self,
        path: Optional[Union[str, Path]],
        overwrite: bool = False,
        progress: Optional[bool] = None,
    ) -> ModelVersionDownloadInfo:
        """
        Download a model file or directory to a local directory if applicable, and return download info
        containing `model_dir` - local path where model was downloaded

        Args:
            path (str): Absolute path of the local filesystem destination directory to which to
                        download the specified models. This directory must already exist.
                        If unspecified, the models will either be downloaded to a new
                        uniquely-named directory on the local filesystem.
            overwrite (bool): If True it will overwrite the file if it is already present in the download directory else
                              it will throw an error
            progress (bool): value to show progress bar, defaults to None.

        Returns:
            ModelVersionDownloadInfo:  Download Info instance containing
                `model_dir` (path to downloaded model folder) and other metadata

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            model_version = client.get_model_version_by_fqn(fqn="<your-model-fqn>")
            download_info = model_version.download(path="<your-desired-download-path>")
            print(download_info.model_dir)
            ```
        """
        download_info = self._download(
            path=path, overwrite=overwrite, progress=progress
        )
        return download_info

    def delete(self) -> bool:
        """
        Deletes the current instance of the ModelVersion hence deleting the current version.

        Returns:
            True if model was deleted successfully

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            model_version = client.get_model_version_by_fqn(fqn="<your-model-fqn>")
            model_version.delete()
            ```
        """
        self._ensure_not_deleted()
        self._mlfoundry_artifacts_api.delete_artifact_version_post(
            delete_artifact_versions_request_dto=DeleteArtifactVersionsRequestDto(
                id=self._model_version.id
            )
        )
        self._deleted = True
        return True

    def update(self):
        """
        Updates the current instance of the ModelVersion hence updating the current version.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            model_version = client.get_model_version_by_fqn(fqn="<your-model-fqn>")
            model_version.description = 'This is the new description'
            model_version.update()
            ```
        """
        self._ensure_not_deleted()
        if self._model_version.manifest:
            self._model_version.manifest.description = self.description
            self._model_version.manifest.metadata = self.metadata
            self._model_version.manifest.environment = self.environment
            self._model_version.manifest.framework = (
                Framework.from_dict(self.framework.dict()) if self.framework else None
            )
            self._model_version.manifest.version_alias = self.version_alias
        try:
            _model_version = self._mlfoundry_artifacts_api.update_model_version_post(
                update_model_version_request_dto=UpdateModelVersionRequestDto(
                    id=self._model_version.id,
                    description=self.description,
                    artifact_metadata=self.metadata,
                    manifest=self._model_version.manifest,
                )
            )
        except Exception:
            # rollback edits to internal object
            self._refetch_model_version(reset_mutable_attrs=False)
            raise
        else:
            self._model_version = _model_version.model_version
            self._set_mutable_attrs()


def _log_model_version(  # noqa: C901
    run: Optional["MlFoundryRun"],
    name: str,
    model_file_or_folder: Union[str, BlobStorageDirectory],
    ml_repo: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    step: Optional[int] = 0,
    progress: Optional[bool] = None,
    framework: Optional[Union[str, ModelFramework, "ModelFrameworkType"]] = None,
    environment: Optional[ModelVersionEnvironment] = None,
) -> ModelVersion:
    if not isinstance(model_file_or_folder, (str, BlobStorageDirectory)):
        raise MlFoundryException(
            "model_file_or_folder should be of type str or BlobStorageDirectory"
        )

    if not run and not ml_repo:
        raise MlFoundryException("Exactly one of run, ml_repo should be passed")

    if run:
        mlfoundry_artifacts_api = run._mlfoundry_artifacts_api
        repos = client.ml_repos.get(id=run._experiment_id)
        ml_repo = repos.data.manifest.name
        ml_repo_id = run._experiment_id
    else:
        assert ml_repo is not None
        api_client = _get_api_client()
        mlfoundry_artifacts_api = MlfoundryArtifactsApi(api_client=api_client)
        result = list(client.ml_repos.list(name=ml_repo, limit=1))[0]
        ml_repo_id = result.id

    step = step or 0
    total_size = None
    metadata = metadata or {}
    metadata = set_tfy_internal_metadata(metadata)

    _validate_description(description)
    _validate_artifact_metadata(metadata)

    if isinstance(model_file_or_folder, str):
        logger.info("Logging model and additional files, this might take a while ...")
        temp_dir = tempfile.TemporaryDirectory(prefix="truefoundry-")
        try:
            logger.info("Adding model file/folder to model version content")
            temp_dest_to_src_map = _copy_additional_files(
                root_dir=temp_dir.name,
                files_dir="",
                model_dir=None,
                additional_files=[(model_file_or_folder, "")],
                ignore_model_dir_dest_conflict=True,
            )

        except Exception as e:
            temp_dir.cleanup()
            raise MlFoundryException("Failed to log model") from e

    # create entry
    _create_artifact_version_response = (
        mlfoundry_artifacts_api.create_artifact_version_post(
            create_artifact_version_request_dto=CreateArtifactVersionRequestDto(
                experiment_id=int(ml_repo_id),
                artifact_type=ArtifactType.MODEL,
                name=name,
            )
        )
    )
    version_id = _create_artifact_version_response.id
    artifact_storage_root = _create_artifact_version_response.artifact_storage_root
    if isinstance(model_file_or_folder, str):
        # Source is of type TrueFoundryManagedSource
        source = TrueFoundryManagedSource(type="truefoundry", uri=artifact_storage_root)
        artifacts_repo = MlFoundryArtifactsRepository(
            artifact_identifier=ArtifactIdentifier(
                artifact_version_id=uuid.UUID(version_id)
            ),
            api_client=mlfoundry_artifacts_api.api_client,
        )
        total_size = calculate_total_size(list(temp_dest_to_src_map.values()))
        try:
            logger.info(
                "Packaging and uploading files to remote with Total Size: %.6f MB",
                total_size / 1000000.0,
            )
            src_dest_pairs = _get_src_dest_pairs(
                root_dir=temp_dir.name, dest_to_src_map=temp_dest_to_src_map
            )
            artifacts_repo.log_artifacts(
                src_dest_pairs=src_dest_pairs, progress=progress
            )
        except Exception as e:
            mlfoundry_artifacts_api.notify_failure_post(
                notify_artifact_version_failure_dto=NotifyArtifactVersionFailureDto(
                    id=version_id
                )
            )
            raise MlFoundryException("Failed to log model") from e
        finally:
            temp_dir.cleanup()
    elif isinstance(model_file_or_folder, BlobStorageDirectory):
        source = ExternalBlobStorageSource(
            type="external", uri=model_file_or_folder.uri
        )
    else:
        raise MlFoundryException("Invalid model_file_or_folder provided")

    if total_size is not None and total_size > 0:
        metadata[ARTIFACT_METADATA_TRUEFOUNDRY_KEY]["artifact_size"] = total_size

    _source_cls = get_autogen_type(ModelManifest, "source")
    # Auto fetch the framework & environment details if not provided
    framework = _ModelFramework.to_model_framework_type(framework)
    if framework and isinstance(model_file_or_folder, str):
        auto_update_model_framework_details(
            framework=framework, model_file_or_folder=model_file_or_folder
        )
    environment = environment or ModelVersionEnvironment()
    auto_update_environment_details(environment=environment, framework=framework)

    model_manifest = ModelManifest(
        name=name,
        ml_repo=ml_repo,
        description=description,
        metadata=metadata,
        source=_source_cls.from_dict(source.dict()),
        framework=Framework.from_dict(framework.dict()) if framework else None,
        environment=environment,
        step=step,
        run_id=run.run_id if run else None,
    )
    _manifest_cls = get_autogen_type(FinalizeArtifactVersionRequestDto, "manifest")
    artifact_version_response = mlfoundry_artifacts_api.finalize_artifact_version_post(
        finalize_artifact_version_request_dto=FinalizeArtifactVersionRequestDto(
            id=version_id,
            run_uuid=run.run_id if run else None,
            artifact_size=total_size,
            artifact_metadata=metadata,
            internal_metadata=None,
            step=model_manifest.step,
            manifest=_manifest_cls.from_dict(model_manifest.to_dict()),
        )
    )
    return ModelVersion.from_fqn(fqn=artifact_version_response.artifact_version.fqn)


def infer_signature(
    model_input: Any = None,
    model_output: Optional[
        Union["pd.DataFrame", "np.ndarray", Dict[str, "np.ndarray"]]
    ] = None,
    params: Optional[Dict[str, Any]] = None,
):
    return _infer_signature(
        model_input=model_input, model_output=model_output, params=params
    )
