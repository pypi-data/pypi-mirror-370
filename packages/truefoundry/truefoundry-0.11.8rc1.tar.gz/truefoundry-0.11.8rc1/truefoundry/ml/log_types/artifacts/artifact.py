import copy
import datetime
import json
import os
import tempfile
import uuid
import warnings
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, NamedTuple, Optional, Union

from truefoundry import client
from truefoundry.common.warnings import TrueFoundryDeprecationWarning
from truefoundry.ml._autogen.client import (  # type: ignore[attr-defined]
    ArtifactDto,
    ArtifactManifest,
    ArtifactType,
    ArtifactVersionDto,
    CreateArtifactVersionRequestDto,
    DeleteArtifactVersionsRequestDto,
    ExternalBlobStorageSource,
    FinalizeArtifactVersionRequestDto,
    MlfoundryArtifactsApi,
    NotifyArtifactVersionFailureDto,
    TrueFoundryManagedSource,
    UpdateArtifactVersionRequestDto,
)
from truefoundry.ml.artifact.truefoundry_artifact_repo import (
    ArtifactIdentifier,
    MlFoundryArtifactsRepository,
)
from truefoundry.ml.exceptions import MlFoundryException
from truefoundry.ml.log_types.artifacts.constants import (
    ARTIFACT_METADATA_TRUEFOUNDRY_KEY,
    INTERNAL_METADATA_PATH,
)
from truefoundry.ml.log_types.artifacts.utils import (
    _get_src_dest_pairs,
    _validate_artifact_metadata,
    _validate_description,
    calculate_total_size,
    get_autogen_type,
    set_tfy_internal_metadata,
)
from truefoundry.ml.logger import logger
from truefoundry.ml.session import _get_api_client
from truefoundry.pydantic_v1 import BaseModel, Extra, StrictStr

if TYPE_CHECKING:
    from truefoundry.ml.mlfoundry_run import MlFoundryRun


class ArtifactPath(NamedTuple):
    src: str
    dest: Optional[str] = None


class BlobStorageDirectory(BaseModel):
    uri: StrictStr


class ArtifactVersionInternalMetadata(BaseModel):
    class Config:
        extra = Extra.allow

    files_dir: str  # relative to root


class ArtifactVersionDownloadInfo(BaseModel):
    download_dir: str


class ArtifactVersion:
    def __init__(
        self,
        artifact_version: ArtifactVersionDto,
        artifact: ArtifactDto,
    ) -> None:
        self._api_client = _get_api_client()
        self._mlfoundry_artifacts_api = MlfoundryArtifactsApi(
            api_client=self._api_client
        )
        self._artifact_version: ArtifactVersionDto = artifact_version
        self._artifact: ArtifactDto = artifact
        self._deleted = False
        self._description: str = ""
        self._metadata: Dict[str, Any] = {}
        self._version_alias: Optional[str] = None
        self._set_mutable_attrs()

    @classmethod
    def from_fqn(cls, fqn: str) -> "ArtifactVersion":
        """
        Get the version of an Artifact to download contents or load them in memory

        Args:
            fqn (str): Fully qualified name of the artifact version.

        Returns:
            ArtifactVersion: An ArtifactVersion instance of the artifact

        Examples:

            ```python
            from truefoundry.ml import get_client, ArtifactVersion

            client = get_client()
            artifact_version = ArtifactVersion.from_fqn(fqn="<artifact-fqn>")
            ```
        """
        api_client = _get_api_client()
        mlfoundry_artifacts_api = MlfoundryArtifactsApi(api_client=api_client)
        _artifact_version = mlfoundry_artifacts_api.get_artifact_version_by_fqn_get(
            fqn=fqn
        )
        artifact_version = _artifact_version.artifact_version
        _artifact = mlfoundry_artifacts_api.get_artifact_by_id_get(
            id=artifact_version.artifact_id
        )
        return cls(
            artifact_version=_artifact_version.artifact_version,
            artifact=_artifact.artifact,
        )

    def _ensure_not_deleted(self):
        if self._deleted:
            raise MlFoundryException(
                "Artifact Version was deleted, cannot access a deleted version"
            )

    def _set_mutable_attrs(self):
        if self._artifact_version.manifest:
            manifest = self._artifact_version.manifest.actual_instance
            self._description = manifest.description or ""
            self._metadata = copy.deepcopy(manifest.metadata)
            self._version_alias = manifest.version_alias or None
        else:
            self._description = self._artifact_version.description or ""
            self._metadata = copy.deepcopy(
                self._artifact_version.artifact_metadata or {}
            )
            self._version_alias = None

    def _refetch_artifact_version(self, reset_mutable_attrs: bool = True):
        _artifact_version = (
            self._mlfoundry_artifacts_api.get_artifact_version_by_id_get(
                id=self._artifact_version.id
            )
        )
        self._artifact_version = _artifact_version.artifact_version
        if reset_mutable_attrs:
            self._set_mutable_attrs()

    def __repr__(self):
        return f"{self.__class__.__name__}(fqn={self.fqn!r})"

    def _get_artifacts_repo(self):
        return MlFoundryArtifactsRepository(
            artifact_identifier=ArtifactIdentifier(
                artifact_version_id=uuid.UUID(self._artifact_version.id)
            ),
            api_client=self._api_client,
        )

    @property
    def name(self) -> str:
        """Get the name of the artifact"""
        return self._artifact.name

    @property
    def artifact_fqn(self) -> str:
        """Get fqn of the artifact"""
        return self._artifact.fqn

    @property
    def version(self) -> int:
        """Get version information of the artifact"""
        return self._artifact_version.version

    @property
    def fqn(self) -> str:
        """Get fqn of the current artifact version"""
        return self._artifact_version.fqn

    @property
    def step(self) -> Optional[int]:
        """Get the step in which artifact was created"""
        if self._artifact_version.manifest:
            return self._artifact_version.manifest.actual_instance.step
        return self._artifact_version.step

    @property
    def description(self) -> str:
        """Get description of the artifact"""
        return self._description

    @description.setter
    def description(self, value: str):
        """set the description of the artifact"""
        _validate_description(value)
        self._description = value

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata for the current artifact"""
        return self._metadata

    @metadata.setter
    def metadata(self, value: Dict[str, Any]):
        """set the metadata for current artifact"""
        _validate_artifact_metadata(value)
        self._metadata = copy.deepcopy(value)

    @property
    def version_alias(self) -> Optional[str]:
        """
        Get version alias for the current artifact version
        """
        if not self._artifact_version.manifest:
            warnings.warn(
                message="This artifact version was created using an older serialization format. version alias does not exist",
                category=TrueFoundryDeprecationWarning,
                stacklevel=2,
            )
        return self._version_alias

    @version_alias.setter
    def version_alias(self, value: Optional[str]):
        """
        Set the version alias for current artifact version
        """
        if not self._artifact_version.manifest:
            warnings.warn(
                message="This artifact version was created using an older serialization format. version alias will not be updated",
                category=TrueFoundryDeprecationWarning,
                stacklevel=2,
            )
            return
        self._version_alias = value

    @property
    def created_at(self) -> Optional[datetime.datetime]:
        """Get the time at which artifact was created"""
        return self._artifact_version.created_at

    @property
    def updated_at(self) -> Optional[datetime.datetime]:
        """Get the information about when the artifact was updated"""
        return self._artifact_version.updated_at

    def raw_download(
        self,
        path: Optional[Union[str, Path]],
        overwrite: bool = False,
        progress: Optional[bool] = None,
    ) -> str:
        """
        Download an artifact file or directory to a local directory if applicable, and return a
        local path for it.

        Args:
            path (str): Absolute path of the local filesystem destination directory to which to
                        download the specified artifacts. This directory must already exist.
                        If unspecified, the artifacts will either be downloaded to a new
                        uniquely-named directory on the local filesystem.
            overwrite (bool): If True it will overwrite the file if it is already present in the download directory else
                              it will throw an error
            progress (bool): value to show progress bar, defaults to None.

        Returns:
            path:  Absolute path of the local filesystem location containing the desired artifacts.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            artifact_version = client.get_artifact_version_by_fqn(fqn="<your-artifact-fqn>")
            artifact_version.raw_download(path="<your-desired-download-path>")
            ```
        """
        logger.info(
            "Downloading artifact version contents, this might take a while ..."
        )
        artifacts_repo = self._get_artifacts_repo()
        return artifacts_repo.download_artifacts(
            artifact_path="", dst_path=path, overwrite=overwrite, progress=progress
        )

    def _download(
        self,
        path: Optional[Union[str, Path]],
        overwrite: bool = False,
        progress: Optional[bool] = None,
    ) -> ArtifactVersionDownloadInfo:
        self._ensure_not_deleted()
        download_dir = self.raw_download(
            path=path, overwrite=overwrite, progress=progress
        )
        if self._artifact_version.manifest:
            download_info = ArtifactVersionDownloadInfo(
                download_dir=download_dir,
            )
            return download_info

        internal_metadata_path = os.path.join(download_dir, INTERNAL_METADATA_PATH)
        if not os.path.exists(internal_metadata_path):
            raise MlFoundryException(
                "Artifact version seems to be corrupted or in invalid format due to missing artifact metadata. "
                "You can still use .raw_download(path='/your/path/here') to download and inspect files."
            )
        with open(internal_metadata_path) as f:
            internal_metadata = ArtifactVersionInternalMetadata.parse_obj(json.load(f))
        download_path = os.path.join(download_dir, internal_metadata.files_dir)
        return ArtifactVersionDownloadInfo(download_dir=download_path)

    def download(
        self,
        path: Optional[Union[str, Path]] = None,
        overwrite: bool = False,
        progress: Optional[bool] = None,
    ) -> str:
        """
        Download an artifact file or directory to a local directory if applicable, and return a
        local path for it.

        Args:
            path (str): Absolute path of the local filesystem destination directory to which to
                        download the specified artifacts. This directory must already exist.
                        If unspecified, the artifacts will either be downloaded to a new
                        uniquely-named directory on the local filesystem or will be returned
                        directly in the case of the Local ArtifactRepository.
            overwrite (bool): If True it will overwrite the file if it is already present in the download directory else
                              it will throw an error
            progress (bool): value to show progress bar, defaults to None.

        Returns:
            path:  Absolute path of the local filesystem location containing the desired artifacts.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            artifact_version = client.get_artifact_version_by_fqn(fqn="<your-artifact-fqn>")
            artifact_version.download(path="<your-desired-download-path>")
            ```
        """
        download_path = self._download(
            path=path, overwrite=overwrite, progress=progress
        )
        return download_path.download_dir

    def delete(self) -> bool:
        """
        Deletes the current instance of the ArtifactVersion hence deleting the current version.

        Returns:
            True if artifact was deleted successfully

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            artifact_version = client.get_artifact_version_by_fqn(fqn="<your-artifact-fqn>")
            artifact_version.delete()
            ```
        """
        self._ensure_not_deleted()
        self._mlfoundry_artifacts_api.delete_artifact_version_post(
            delete_artifact_versions_request_dto=DeleteArtifactVersionsRequestDto(
                id=self._artifact_version.id
            )
        )
        self._deleted = True
        return True

    def update(self):
        """
        Updates the current instance of the ArtifactVersion hence updating the current version.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            artifact_version = client.get_artifact_version_by_fqn(fqn="<your-artifact-fqn>")
            artifact_version.description = 'This is the new description'
            artifact_version.update()
            ```
        """
        self._ensure_not_deleted()
        if self._artifact_version.manifest:
            manifest = self._artifact_version.manifest.actual_instance
            assert isinstance(manifest, ArtifactManifest)
            manifest.description = self.description
            manifest.metadata = self.metadata
            manifest.version_alias = self.version_alias
        else:
            manifest = None
        try:
            _manifest_cls = get_autogen_type(
                UpdateArtifactVersionRequestDto, "manifest"
            )
            _artifact_version = (
                self._mlfoundry_artifacts_api.update_artifact_version_post(
                    update_artifact_version_request_dto=UpdateArtifactVersionRequestDto(
                        id=self._artifact_version.id,
                        description=self.description,
                        artifact_metadata=self.metadata,
                        manifest=_manifest_cls.from_dict(manifest.to_dict())
                        if manifest
                        else None,
                    )
                )
            )
        except Exception:
            # rollback edits to internal object
            self._refetch_artifact_version(reset_mutable_attrs=False)
            raise
        else:
            self._artifact_version = _artifact_version.artifact_version
            self._set_mutable_attrs()


def _log_artifact_version_helper(
    run: Optional["MlFoundryRun"],
    name: str,
    artifact_type: ArtifactType,
    artifact_dir: Union[tempfile.TemporaryDirectory, BlobStorageDirectory],
    dest_to_src_map: Dict[str, str],
    ml_repo: Optional[str] = None,
    description: Optional[str] = None,
    internal_metadata: Optional[BaseModel] = None,
    metadata: Optional[Dict[str, Any]] = None,
    step: int = 0,
    progress: Optional[bool] = None,
) -> ArtifactVersion:
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

    metadata = metadata or {}
    metadata = set_tfy_internal_metadata(metadata)

    _validate_description(description)
    _validate_artifact_metadata(metadata)

    assert mlfoundry_artifacts_api is not None
    _create_artifact_response = mlfoundry_artifacts_api.create_artifact_version_post(
        create_artifact_version_request_dto=CreateArtifactVersionRequestDto(
            experiment_id=int(ml_repo_id),
            name=name,
            artifact_type=artifact_type,
        )
    )
    version_id = _create_artifact_response.id
    artifact_storage_root = _create_artifact_response.artifact_storage_root
    total_size = None

    if isinstance(artifact_dir, tempfile.TemporaryDirectory):
        # Source is of type TrueFoundryManagedSource
        source = TrueFoundryManagedSource(type="truefoundry", uri=artifact_storage_root)
        artifacts_repo = MlFoundryArtifactsRepository(
            artifact_identifier=ArtifactIdentifier(
                artifact_version_id=uuid.UUID(version_id),
            ),
            api_client=mlfoundry_artifacts_api.api_client,
        )

        total_size = calculate_total_size(list(dest_to_src_map.values()))
        try:
            logger.info(
                "Packaging and uploading files to remote with size: %.6f MB",
                total_size / 1000000.0,
            )
            src_dest_pairs = _get_src_dest_pairs(
                root_dir=artifact_dir.name, dest_to_src_map=dest_to_src_map
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
            raise MlFoundryException("Failed to log Artifact") from e
        finally:
            artifact_dir.cleanup()
    elif isinstance(artifact_dir, BlobStorageDirectory):
        source = ExternalBlobStorageSource(type="external", uri=artifact_dir.uri)
    else:
        raise MlFoundryException("Invalid artifact_dir provided")

    if total_size is not None and total_size > 0:
        metadata[ARTIFACT_METADATA_TRUEFOUNDRY_KEY]["artifact_size"] = total_size

    artifact_manifest = None
    if artifact_type == ArtifactType.ARTIFACT:
        _source_cls = get_autogen_type(ArtifactManifest, "source")
        artifact_manifest = ArtifactManifest(
            name=name,
            ml_repo=ml_repo,
            description=description,
            metadata=metadata,
            source=_source_cls.from_dict(source.dict()),
            step=step,
            run_id=run.run_id if run else None,
        )
    _manifest_cls = get_autogen_type(FinalizeArtifactVersionRequestDto, "manifest")

    finalize_artifact_version_request_dto = FinalizeArtifactVersionRequestDto(
        id=version_id,
        run_uuid=run.run_id if run else None,
        internal_metadata=internal_metadata.dict()
        if internal_metadata is not None
        else {},
        artifact_metadata=metadata,
        data_path=INTERNAL_METADATA_PATH if internal_metadata else None,
        step=step,
        artifact_size=total_size,
        manifest=_manifest_cls.from_dict(artifact_manifest.to_dict())
        if artifact_manifest
        else None,
    )
    _artifact_version = mlfoundry_artifacts_api.finalize_artifact_version_post(
        finalize_artifact_version_request_dto=finalize_artifact_version_request_dto
    )
    return ArtifactVersion.from_fqn(fqn=_artifact_version.artifact_version.fqn)
