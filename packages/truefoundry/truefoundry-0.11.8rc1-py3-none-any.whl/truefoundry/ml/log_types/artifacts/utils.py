import json
import logging
import os
import posixpath
import typing
from pathlib import Path, PureWindowsPath
from typing import Any, Dict, List, Optional, Sequence, Tuple, Type, Union

from truefoundry.ml.exceptions import MlFoundryException
from truefoundry.ml.log_types.artifacts.constants import (
    ARTIFACT_METADATA_TRUEFOUNDRY_KEY,
    DESCRIPTION_MAX_LENGTH,
    TFY_INTERNAL_APPLICATION_FQN_ENV_VAR,
    TFY_INTERNAL_APPLICATION_ID_ENV_VAR,
    TFY_INTERNAL_APPLICATION_NAME_ENV_VAR,
    TFY_INTERNAL_APPLICATION_VERSION_ENV_VAR,
    TFY_INTERNAL_JOB_RUN_NAME_ENV_VAR,
)
from truefoundry.pydantic_v1 import BaseModel

logger = logging.getLogger(__name__)


def to_unix_path(path):
    path = os.path.normpath(path)
    if os.path.sep == "\\":
        path = PureWindowsPath(path).as_posix()
    return path


def _copy_tree(
    root_dir: str, src_path: str, dest_path: str, dest_to_src: Dict[str, str]
):
    os.makedirs(dest_path, exist_ok=True)
    for item in os.listdir(src_path):
        src = os.path.join(src_path, item)
        dest = os.path.join(dest_path, item)
        if os.path.isdir(src):
            _copy_tree(
                root_dir=root_dir,
                src_path=src,
                dest_path=dest,
                dest_to_src=dest_to_src,
            )
        else:
            dest_to_src[dest] = src


def is_destination_path_dirlike(dest_path) -> bool:
    if not dest_path:
        return True

    if dest_path.endswith(os.sep) or dest_path.endswith(posixpath.sep):
        return True

    if os.path.exists(dest_path) and os.path.isdir(dest_path):
        return True

    return False


def get_single_file_path_if_only_one_in_directory(path: str) -> Optional[str]:
    """
    Get the filename from a path, or return a filename from a directory if a single file exists.
    Args:
        path: The file or folder path.
    Returns:
        Optional[str]: The filename or None if no files are found or multiple files are found.
    """
    # If it's already a file, return it as-is
    if os.path.isfile(path):
        return path

    # If it's a directory, check if it contains a single file
    if is_destination_path_dirlike(path):
        all_files: List[str] = []
        for root, _, files in os.walk(path):
            # Collect all files found in any subdirectory
            all_files.extend(os.path.join(root, f) for f in files)
            # If more than one file is found, stop early
            if len(all_files) > 1:
                return None

        # If only one file is found, return it
        if len(all_files) == 1:
            return all_files[0]

    return None  # No file found or Multiple files found


def _copy_additional_files(
    root_dir: str,
    files_dir: str,  # relative to root dir e.g. "files/"
    model_dir: Optional[str],  # relative to files_dir e.g "model/"
    additional_files: Sequence[Tuple[Union[str, Path], Optional[str]]],
    ignore_model_dir_dest_conflict: bool = False,
    existing_dest_to_src_map: Optional[Dict[str, str]] = None,
) -> Dict[str, str]:
    """
    File copying examples:
        # non ambiguous
        # a.txt -> /tmp/                            result /tmp/a.txt
        # a.txt -> /tmp/a/                          result /tmp/a/a.txt
        # a.txt -> /tmp/a/b/c/d.txt                 result /tmp/a/b/c/d.txt
        # .gitignore -> /tmp/.gitignore             result /tmp/.gitignore

        # ambiguous but destination directory exists
        # a.txt -> /tmp                             result /tmp/a.txt
        # a.txt -> /tmp/a (and /tmp/a/ exists)      result /tmp/a/a.txt

        # ambiguous - when the destination can't be reliably distinguished as a directory
        # a -> /tmp/a                                result /tmp/a
        # a -> /tmp/b                                result /tmp/b
        # a -> /tmp/a.txt                            result /tmp/a.txt
        # .gitignore -> /tmp/.gitinclude             result /tmp/.gitinclude
        # a.txt -> /tmp/a                            result /tmp/a
    """
    dest_to_src = existing_dest_to_src_map or {}
    for src_path, dest_path in additional_files:
        src_path = str(src_path)
        if not os.path.exists(src_path):
            raise MlFoundryException(
                f"Source path {src_path!r} in `additional_files` does not exist."
            )
        dest_path = dest_path or ""
        normalized_path = os.path.normpath(dest_path)
        if dest_path.endswith(os.sep) or dest_path.endswith(posixpath.sep):
            normalized_path += os.sep
        dest_path = normalized_path.lstrip(os.sep)

        if (
            model_dir
            and dest_path.startswith(model_dir)
            and not ignore_model_dir_dest_conflict
        ):
            logger.warning(
                f"Destination path {dest_path!r} in `additional_files` conflicts with "
                f"reserved path {model_dir!r}/ which is being used to store the model. "
                f"This might cause errors"
            )

        files_abs_dir = os.path.join(root_dir, files_dir)
        dest_abs_path = os.path.join(files_abs_dir, dest_path)

        if os.path.isfile(src_path):
            _src = src_path
            if is_destination_path_dirlike(dest_abs_path):
                os.makedirs(dest_abs_path, exist_ok=True)
                dest_abs_path = os.path.join(dest_abs_path, os.path.basename(_src))
            else:
                os.makedirs(os.path.dirname(dest_abs_path), exist_ok=True)
            _dst = os.path.relpath(dest_abs_path, files_abs_dir)
            logger.info(f"Adding file {_src} as /{_dst}")
            dest_to_src[dest_abs_path] = src_path
        elif os.path.isdir(src_path):
            os.makedirs(dest_abs_path, exist_ok=True)
            _src = src_path.rstrip("/")
            _dst = os.path.relpath(dest_abs_path, files_abs_dir).rstrip("/")
            logger.info(f"Adding contents of {_src}/ to /{_dst}/")
            _copy_tree(
                root_dir=root_dir,
                src_path=src_path,
                dest_path=dest_abs_path,
                dest_to_src=dest_to_src,
            )

    return dest_to_src


def _make_dest_to_src_map_from_dir(root_dir: str) -> Dict[str, str]:
    dest_to_src_map = {}
    for root, _, files in os.walk(root_dir):
        for file in files:
            src = os.path.join(root, file)
            dest = src
            dest_to_src_map[dest] = src
    return dest_to_src_map


def _get_src_dest_pairs(
    root_dir: str,
    dest_to_src_map: Dict[str, str],
) -> Sequence[Tuple[str, str]]:
    src_dest_pairs = [
        (src_path, to_unix_path(os.path.relpath(dest_abs_path, root_dir)))
        for dest_abs_path, src_path in dest_to_src_map.items()
    ]
    return src_dest_pairs


def _validate_description(description: Optional[str]):
    if description is not None:
        if not isinstance(description, str):
            raise MlFoundryException(
                "`description` must be either `None` or type `str`"
            )
        if len(description) > DESCRIPTION_MAX_LENGTH:
            raise MlFoundryException(
                f"`description` cannot be longer than {DESCRIPTION_MAX_LENGTH} characters"
            )


def _validate_artifact_metadata(metadata: Dict[str, Any]):
    if not isinstance(metadata, dict):
        raise MlFoundryException("`metadata` must be json serializable dict")
    try:
        json.dumps(metadata)
    except ValueError as ve:
        raise MlFoundryException("`metadata` must be json serializable dict") from ve


def calculate_total_size(
    paths: Sequence[str],
):
    """
    Tells about the size of the artifact

    Args:
        paths (str): list of paths to include in total size calculation

    Returns:
        total size of the artifact
    """
    return sum(os.stat(os.path.realpath(file_path)).st_size for file_path in paths)


def get_autogen_type(parent_type: Type[BaseModel], field_name: str) -> Type[BaseModel]:
    type_ = typing.get_type_hints(parent_type)[field_name]
    origin = typing.get_origin(type_)

    if origin is None:
        return type_
    elif origin is typing.Union:
        args = typing.get_args(type_)
        if len(args) == 2 and args[-1] is type(None):
            return args[0]

    raise NotImplementedError(f"Cannot extract main type from {type_}")


def set_tfy_internal_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    if ARTIFACT_METADATA_TRUEFOUNDRY_KEY not in metadata:
        metadata[ARTIFACT_METADATA_TRUEFOUNDRY_KEY] = {}
    elif not isinstance(metadata[ARTIFACT_METADATA_TRUEFOUNDRY_KEY], dict):
        return metadata

    tfy_metadata = metadata[ARTIFACT_METADATA_TRUEFOUNDRY_KEY]
    created_by_key = "created_by"
    if created_by_key not in tfy_metadata:
        tfy_metadata[created_by_key] = {}
    elif not isinstance(tfy_metadata[created_by_key], dict):
        return metadata

    tfy_internal_metadata = {
        "application_id": os.environ.get(TFY_INTERNAL_APPLICATION_ID_ENV_VAR),
        "application_fqn": os.environ.get(TFY_INTERNAL_APPLICATION_FQN_ENV_VAR),
        "application_name": os.environ.get(TFY_INTERNAL_APPLICATION_NAME_ENV_VAR),
        "application_version": os.environ.get(TFY_INTERNAL_APPLICATION_VERSION_ENV_VAR),
        "job_run_name": os.environ.get(TFY_INTERNAL_JOB_RUN_NAME_ENV_VAR),
    }
    created_by_metadata = tfy_metadata[created_by_key]
    for key, value in tfy_internal_metadata.items():
        if key not in created_by_metadata and value is not None:
            created_by_metadata[key] = value
    return metadata
