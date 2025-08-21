import collections
import tempfile
from typing import TYPE_CHECKING, Any, Dict, List, Optional, Tuple, Union

from truefoundry.ml._autogen.client import (  # type: ignore[attr-defined]
    ArtifactType,
)
from truefoundry.ml.exceptions import MlFoundryException
from truefoundry.ml.log_types.artifacts.artifact import (
    ArtifactPath,
    ArtifactVersion,
    _log_artifact_version_helper,
)
from truefoundry.ml.log_types.artifacts.utils import (
    _copy_additional_files,
    _validate_artifact_metadata,
    _validate_description,
)
from truefoundry.ml.logger import logger

if TYPE_CHECKING:
    from truefoundry.ml.mlfoundry_run import MlFoundryRun


def _log_artifact_version(
    run: Optional["MlFoundryRun"],
    name: str,
    artifact_paths: List[Union[ArtifactPath, Tuple[str, Optional[str]], Tuple[str]]],
    ml_repo: Optional[str] = None,
    description: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    step: Optional[int] = 0,
    progress: Optional[bool] = None,
) -> ArtifactVersion:
    if not run and not ml_repo:
        raise MlFoundryException("Exactly one of run, ml_repo should be passed")
    for i, artifact_path in enumerate(artifact_paths):
        if isinstance(artifact_path, ArtifactPath):
            continue
        elif isinstance(artifact_path, collections.abc.Sequence) and (
            0 < len(artifact_path) <= 2
        ):
            artifact_paths[i] = ArtifactPath(*artifact_path)
        else:
            raise ValueError(
                "`artifact_path` should be an instance of `truefoundry.ml.ArtifactPath` or a tuple "
                "of (src, dest) path strings"
            )

    metadata = metadata or {}
    step = step or 0  # TODO (chiragjn): remove Optional from step

    _validate_description(description)
    _validate_artifact_metadata(metadata)

    logger.info("Logging the artifact, this might take a while ...")
    temp_dir = tempfile.TemporaryDirectory(prefix="truefoundry-")

    try:
        temp_dest_to_src_map = _copy_additional_files(
            root_dir=temp_dir.name,
            files_dir="",
            model_dir=None,
            additional_files=artifact_paths,
        )

    # TODO(nikp1172) verify error message when artifact doesn't exist
    except Exception as e:
        temp_dir.cleanup()
        raise MlFoundryException("Failed to log artifact") from e

    return _log_artifact_version_helper(
        run=run,
        ml_repo=ml_repo,
        name=name,
        artifact_type=ArtifactType.ARTIFACT,
        artifact_dir=temp_dir,
        dest_to_src_map=temp_dest_to_src_map,
        description=description,
        internal_metadata=None,
        metadata=metadata,
        step=step,
        progress=progress,
    )
