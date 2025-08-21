from typing import Callable, Dict

from truefoundry.deploy.builder.builders import (
    dockerfile,
    tfy_notebook_buildpack,
    tfy_python_buildpack,
    tfy_spark_buildpack,
    tfy_task_pyspark_buildpack,
)

BUILD_REGISTRY: Dict[str, Callable] = {
    "dockerfile": dockerfile.build,
    "tfy-python-buildpack": tfy_python_buildpack.build,
    "tfy-notebook-buildpack": tfy_notebook_buildpack.build,
    "tfy-spark-buildpack": tfy_spark_buildpack.build,
    "task-pyspark-build": tfy_task_pyspark_buildpack.build,
}

__all__ = ["get_builder"]


def get_builder(build_configuration_type: str) -> Callable:
    if build_configuration_type not in BUILD_REGISTRY:
        raise NotImplementedError(f"Builder for {build_configuration_type} not found")

    return BUILD_REGISTRY[build_configuration_type]
