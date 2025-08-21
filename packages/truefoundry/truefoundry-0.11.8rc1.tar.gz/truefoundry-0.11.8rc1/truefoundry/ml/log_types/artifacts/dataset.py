import collections
import copy
import datetime
import tempfile
from typing import Any, Dict, Iterator, List, NamedTuple, Optional, Tuple, Union
from warnings import warn

from truefoundry.ml._autogen.client import (  # type: ignore[attr-defined]
    DatasetDto,
    DeleteDatasetRequestDto,
    MlfoundryArtifactsApi,
    UpdateDatasetRequestDto,
)
from truefoundry.ml.artifact.truefoundry_artifact_repo import (
    ArtifactIdentifier,
    MlFoundryArtifactsRepository,
)
from truefoundry.ml.entities import FileInfo
from truefoundry.ml.exceptions import MlFoundryException
from truefoundry.ml.log_types.artifacts.utils import (
    _copy_additional_files,
    _get_src_dest_pairs,
    _validate_artifact_metadata,
    _validate_description,
    calculate_total_size,
)
from truefoundry.ml.logger import logger
from truefoundry.ml.session import _get_api_client


class DataDirectoryPath(NamedTuple):
    src: str
    dest: Optional[str] = None


class DataDirectory:
    def __init__(self, dataset: DatasetDto) -> None:
        self._api_client = _get_api_client()
        self._mlfoundry_artifacts_api = MlfoundryArtifactsApi(
            api_client=self._api_client
        )
        self._dataset = dataset
        self._description: str = ""
        self._deleted = False
        self._metadata: Dict[str, Any] = {}
        self._set_mutable_attrs()

    @classmethod
    def from_fqn(cls, fqn: str):
        """
        Get the DataDirectory to download contents or load them in memory

        Args:
            fqn (str): Fully qualified name of the data directory.

        Returns:
            DataDirectory: An DataDirectory instance of the artifact

        Examples:

            ```python
            from truefoundry.ml import get_client, DataDirectory

            client = get_client()
            data_directory = DataDirectory.from_fqn(fqn="<data_directory-fqn>")
            ```
        """
        api_client = _get_api_client()
        mlfoundry_artifacts_api = MlfoundryArtifactsApi(api_client=api_client)
        _dataset = mlfoundry_artifacts_api.get_dataset_by_fqn_get(fqn=fqn)
        return cls(_dataset.dataset)

    def __repr__(self):
        return f"{self.__class__.__name__}(fqn={self.fqn!r})"

    def _set_mutable_attrs(self, refetch=False):
        if refetch:
            _dataset = self._mlfoundry_artifacts_api.get_dataset_by_fqn_get(
                fqn=self._dataset.fqn
            )
            self._dataset = _dataset.dataset
        self._description = self._dataset.description or ""
        self._metadata = copy.deepcopy(self._dataset.dataset_metadata)

    def _get_artifacts_repo(self):
        return MlFoundryArtifactsRepository(
            artifact_identifier=ArtifactIdentifier(
                dataset_id=self._dataset.id, dataset_fqn=self._dataset.fqn
            ),
            api_client=self._api_client,
        )

    @property
    def name(self) -> str:
        """Get the name of the DataDirectory"""
        return self._dataset.name

    @property
    def fqn(self) -> str:
        """Get fqn of the DataDirectory"""
        return self._dataset.fqn

    @property
    def storage_root(self) -> str:
        """Get storage_root of the DataDirectory"""
        return self._dataset.storage_root

    @property
    def description(self) -> Optional[str]:
        """Get description of the DataDirectory"""
        return self._description

    @description.setter
    def description(self, value: str):
        """set the description of the DataDirectory"""
        _validate_description(value)
        self._description = value

    @property
    def metadata(self) -> Dict[str, Any]:
        """Get metadata for the current DataDirectory"""
        return self._metadata

    @metadata.setter
    def metadata(self, value: Dict[str, Any]):
        """set the metadata for current DataDirectory"""
        _validate_artifact_metadata(value)
        self._metadata = value

    @property
    def created_at(self) -> datetime.datetime:
        """Get the time at which DataDirectory was created"""
        return self._dataset.created_at

    @property
    def updated_at(self) -> datetime.datetime:
        """Get the information about when the DataDirectory was updated"""
        return self._dataset.updated_at

    def add_files(
        self,
        file_paths: List[
            Union[Tuple[str], Tuple[str, Optional[str]], DataDirectoryPath]
        ],
        progress: Optional[bool] = None,
    ) -> None:
        """Logs File in the `DataDirectory`.

        Args:
            file_paths (List[truefoundry.ml.DataDirectoryPath], optional): A list of pairs
                of (source path, destination path) to add files and folders to the DataDirectory contents.
                The first member of the pair should be a file or directory path and the second member should be
                the path inside the artifact contents to upload to.

                ```python
                from truefoundry.ml import DataDirectoryPath

                data_directory.add_files(
                    file_paths=[
                        DataDirectoryPath("foo.txt", "foo/bar/foo.txt"),
                        DataDirectoryPath("tokenizer/", "foo/tokenizer/"),
                        DataDirectoryPath('bar.text'),
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

        Examples:
            ```python
            import os
            from truefoundry.ml import get_client, DataDirectoryPath

            with open("artifact.txt", "w") as f:
                f.write("hello-world")

            client = get_client()
            data_directory = client.get_data_directory_by_fqn(fqn="<data_directory-fqn>")

            data_directory.add_files(
                file_paths=[DataDirectoryPath('artifact.txt', 'a/b/')]
            )
            ```
        """
        for i, file_path in enumerate(file_paths):
            if isinstance(file_path, DataDirectoryPath):
                continue
            elif isinstance(file_path, collections.abc.Sequence) and (
                0 < len(file_path) <= 2
            ):
                file_paths[i] = DataDirectoryPath(*file_path)
            else:
                raise ValueError(
                    "`file_paths` should be an instance of `truefoundry.ml.DataDirectoryPath` "
                    "or a tuple of (src, dest) path strings"
                )

        logger.info("Adding the files to data_directory, this might take a while ...")
        temp_dir = tempfile.TemporaryDirectory(prefix="truefoundry-")

        try:
            logger.info("Copying the files to add")
            temp_dest_to_src_map = _copy_additional_files(
                root_dir=temp_dir.name,
                files_dir="",
                model_dir=None,
                additional_files=file_paths,
            )

        except Exception as e:
            temp_dir.cleanup()
            raise MlFoundryException("Failed to Add Files to DataDirectory") from e

        artifacts_repo = self._get_artifacts_repo()
        total_size = calculate_total_size(list(temp_dest_to_src_map.values()))
        try:
            logger.info(
                "Packaging and uploading files to remote with size: %.6f MB",
                total_size / 1000000.0,
            )
            src_dest_pairs = _get_src_dest_pairs(
                root_dir=temp_dir.name, dest_to_src_map=temp_dest_to_src_map
            )
            artifacts_repo.log_artifacts(
                src_dest_pairs=src_dest_pairs,
                progress=progress,
            )
        except Exception as e:
            raise MlFoundryException("Failed to Add Files to DataDirectory") from e
        finally:
            temp_dir.cleanup()

    def list_files(
        self,
        path: Optional[str] = None,
    ) -> Iterator[FileInfo]:
        """
        List all the files and folders in the data_directory.

        Args:
            path: The path of directory in data_directory, from which the files are to be listed.

        Returns:
            Iterator[FileInfoDto]: List of FileInfo objects that contain path and file_size attributes.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            data_directory = client.get_data_directory_by_fqn(fqn="<your-artifact-fqn>")
            files = data_directory.list_files()
            for file in files:
                print(file.path)
            ```
        """
        artifacts_repo = self._get_artifacts_repo()
        for file_info_dto in artifacts_repo.list_artifacts(path=path):
            yield FileInfo.from_dto(file_info_dto)

    def download(
        self,
        remote_path: Optional[str] = "",
        path: Optional[str] = None,
        overwrite: bool = False,
        progress: Optional[bool] = None,
        download_path: Optional[str] = "",
    ):
        """
        Download a file or directory to a local directory if applicable, and return a
        local path for it.

        Args:
            download_path: (deprecated) Relative source path to the desired files.
            remote_path: Relative source path to the desired files.
            path: Absolute path of the local filesystem destination directory to which to
                download the specified files. This directory must already exist.
                If unspecified, the files will either be downloaded to a new
                uniquely-named directory.
            overwrite: if to overwrite the files at/inside `dst_path` if they exist
            progress: value to show progress bar, defaults to None.

        Returns:
            str: Absolute path of the local filesystem location containing the desired files or folder.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            data_directory = client.get_data_directory_by_fqn(fqn="<your-data_directory-fqn>")
            data_directory.download(download_path="<your-desired-download-path>")
            ```
        """
        self._ensure_not_deleted()
        artifacts_repo = self._get_artifacts_repo()
        if download_path != "" and remote_path != "":
            raise ValueError(
                "Only one of 'download_path' or 'remote_path' should be specified."
            )

        if download_path != "":
            warn(
                "`download_path` is deprecated, please use `remote_path` instead.",
                DeprecationWarning,
                stacklevel=2,
            )
            remote_path = download_path

        return artifacts_repo.download_artifacts(
            artifact_path=remote_path,
            dst_path=path,
            overwrite=overwrite,
            progress=progress,
        )

    def update(self):
        """
        Updates the current instance of the DataDirectory.

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            data_directory = client.get_data_directory_by_fqn(fqn="<your-data-directory-fqn>")
            data_directory.description = 'This is the new description'
            data_directory.update()
            ```
        """
        self._ensure_not_deleted()
        _dataset = self._mlfoundry_artifacts_api.update_dataset_post(
            update_dataset_request_dto=UpdateDatasetRequestDto(
                fqn=self._dataset.fqn,
                description=self.description,
                dataset_metadata=self.metadata,
            )
        )
        self._dataset = _dataset.dataset
        self._set_mutable_attrs()

    def _ensure_not_deleted(self):
        if self._deleted:
            raise MlFoundryException(
                "Data Directory was deleted, cannot access a deleted version"
            )

    def delete(self, delete_contents: bool = False) -> bool:
        """
        Deletes the current instance of the DataDirectory.

        Args:
            delete_contents: set it to true to delete the contents in storage integration. Default is False.

        Returns:
            True if artifact was deleted successfully

        Examples:

            ```python
            from truefoundry.ml import get_client

            client = get_client()
            dataset = client.get_data_directory_by_fqn(fqn="<your-data-directory-fqn>")
            dataset.delete()
            ```
        """
        self._ensure_not_deleted()
        self._mlfoundry_artifacts_api.delete_dataset_post(
            delete_dataset_request_dto=DeleteDatasetRequestDto(
                id=self._dataset.id, delete_contents=delete_contents
            )
        )
        self._deleted = True
        return True
