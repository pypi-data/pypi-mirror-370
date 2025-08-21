try:
    import fsspec
    from flytekit import task as _
except ImportError:
    print(
        "To use workflows, please run 'pip install truefoundry[workflow]'. "
        "Note: The `workflow` feature is only available for Python 3.9 to 3.12"
    )

from flytekit import conditional
from flytekit.types.directory import FlyteDirectory
from flytekit.types.error.error import FlyteError
from flytekit.types.file import FlyteFile

from truefoundry.common.constants import ENV_VARS
from truefoundry.deploy.v2.lib.patched_models import (
    ContainerTaskConfig,
    PySparkTaskConfig,
    PythonTaskConfig,
    TaskDockerFileBuild,
    TaskPythonBuild,
)
from truefoundry.workflow.container_task import ContainerTask
from truefoundry.workflow.map_task import map_task
from truefoundry.workflow.python_task import PythonFunctionTask
from truefoundry.workflow.remote_filesystem.tfy_signed_url_fs import SignedURLFileSystem
from truefoundry.workflow.task import task
from truefoundry.workflow.workflow import ExecutionConfig, workflow

__all__ = [
    "task",
    "ContainerTask",
    "PythonFunctionTask",
    "map_task",
    "workflow",
    "conditional",
    "FlyteDirectory",
    "TaskDockerFileBuild",
    "TaskPythonBuild",
    "ContainerTaskConfig",
    "PythonTaskConfig",
    "ExecutionConfig",
    "FlyteFile",
    "FlyteError",
    "PySparkTaskConfig",
]


# Register the SignedURLFileSystem implementation for fsspec
if ENV_VARS.TFY_INTERNAL_SIGNED_URL_SERVER_HOST:
    fsspec.register_implementation("s3", SignedURLFileSystem, clobber=True)
    fsspec.register_implementation("gs", SignedURLFileSystem, clobber=True)
    fsspec.register_implementation("abfs", SignedURLFileSystem, clobber=True)
