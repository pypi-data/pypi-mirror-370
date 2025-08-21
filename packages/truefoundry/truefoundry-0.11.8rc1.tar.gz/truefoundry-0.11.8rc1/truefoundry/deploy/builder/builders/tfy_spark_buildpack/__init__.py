import os
import shutil
from tempfile import TemporaryDirectory
from typing import List, Optional

from truefoundry.common.constants import PythonPackageManager
from truefoundry.deploy._autogen.models import DockerFileBuild, SparkBuild
from truefoundry.deploy.builder.builders import dockerfile
from truefoundry.deploy.builder.builders.tfy_spark_buildpack.dockerfile_template import (
    generate_dockerfile_content,
)
from truefoundry.deploy.builder.utils import has_python_package_manager_conf_secret

__all__ = ["generate_dockerfile_content", "build"]


def _convert_to_dockerfile_build_config(
    build_configuration: SparkBuild,
    dockerfile_path: str,
    mount_python_package_manager_conf_secret: bool = False,
) -> DockerFileBuild:
    dockerfile_content = generate_dockerfile_content(
        build_configuration=build_configuration,
        mount_python_package_manager_conf_secret=mount_python_package_manager_conf_secret,
        package_manager=PythonPackageManager.PIP.value,
    )
    with open(dockerfile_path, "w", encoding="utf8") as fp:
        fp.write(dockerfile_content)

    return DockerFileBuild(
        type="dockerfile",
        dockerfile_path=dockerfile_path,
        build_context_path=build_configuration.build_context_path,
    )


def build(
    tag: str,
    build_configuration: SparkBuild,
    extra_opts: Optional[List[str]] = None,
):
    mount_python_package_manager_conf_secret = (
        has_python_package_manager_conf_secret(extra_opts) if extra_opts else False
    )

    # Copy tfy_execute_notebook.py to the build context
    execute_notebook_src = os.path.join(
        os.path.dirname(__file__), "tfy_execute_notebook.py"
    )
    execute_notebook_dst = os.path.join(
        build_configuration.build_context_path, "tfy_execute_notebook.py"
    )

    # Verify the source file exists before copying
    if not os.path.isfile(execute_notebook_src):
        raise FileNotFoundError(f"Required file not found: {execute_notebook_src}")

    # Always copy the file, overwrite if exists
    shutil.copy2(execute_notebook_src, execute_notebook_dst)

    try:
        with TemporaryDirectory() as local_dir:
            docker_build_configuration = _convert_to_dockerfile_build_config(
                build_configuration,
                dockerfile_path=os.path.join(local_dir, "Dockerfile"),
                mount_python_package_manager_conf_secret=mount_python_package_manager_conf_secret,
            )
            dockerfile.build(
                tag=tag,
                build_configuration=docker_build_configuration,
                extra_opts=extra_opts,
            )
    finally:
        # Clean up the copied file if we copied it
        if os.path.exists(execute_notebook_dst):
            try:
                os.remove(execute_notebook_dst)
            except OSError:
                pass  # Ignore errors when cleaning up
