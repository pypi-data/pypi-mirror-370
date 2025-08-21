import os
from tempfile import TemporaryDirectory
from typing import List, Optional

from truefoundry.deploy._autogen.models import DockerFileBuild, PythonBuild
from truefoundry.deploy.builder.builders import dockerfile
from truefoundry.deploy.builder.builders.tfy_python_buildpack.dockerfile_template import (
    generate_dockerfile_content,
)
from truefoundry.deploy.builder.utils import has_python_package_manager_conf_secret

__all__ = ["generate_dockerfile_content", "build"]


def _convert_to_dockerfile_build_config(
    build_configuration: PythonBuild,
    dockerfile_path: str,
    mount_python_package_manager_conf_secret: bool = False,
) -> DockerFileBuild:
    dockerfile_content = generate_dockerfile_content(
        build_configuration=build_configuration,
        mount_python_package_manager_conf_secret=mount_python_package_manager_conf_secret,
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
    build_configuration: PythonBuild,
    extra_opts: Optional[List[str]] = None,
):
    if not build_configuration.python_version:
        raise ValueError(
            "`python_version` is required for `tfy-python-buildpack` builder"
        )
    mount_python_package_manager_conf_secret = (
        has_python_package_manager_conf_secret(extra_opts) if extra_opts else False
    )
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
