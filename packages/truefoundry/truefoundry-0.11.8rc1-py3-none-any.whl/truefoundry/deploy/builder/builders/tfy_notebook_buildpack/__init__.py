import os
from tempfile import TemporaryDirectory
from typing import List, Optional

from truefoundry.deploy._autogen.models import DockerFileBuild
from truefoundry.deploy.builder.builders import dockerfile
from truefoundry.deploy.builder.builders.tfy_notebook_buildpack.dockerfile_template import (
    NotebookImageBuild,
    generate_dockerfile_content,
)
from truefoundry.deploy.builder.utils import has_python_package_manager_conf_secret

__all__ = ["generate_dockerfile_content", "build"]


def _convert_to_dockerfile_build_config(
    build_configuration: NotebookImageBuild,
    local_dir: str,
    mount_pip_conf_secret: bool = False,
) -> DockerFileBuild:
    dockerfile_content = generate_dockerfile_content(
        build_configuration=build_configuration,
        local_dir=local_dir,
        mount_pip_conf_secret=mount_pip_conf_secret,
    )
    dockerfile_path = os.path.join(local_dir, "Dockerfile")
    with open(dockerfile_path, "w", encoding="utf8") as fp:
        fp.write(dockerfile_content)
    return DockerFileBuild(
        type="dockerfile",
        dockerfile_path=dockerfile_path,
        build_context_path=local_dir,
    )


def build(
    tag: str,
    build_configuration: NotebookImageBuild,
    extra_opts: Optional[List[str]] = None,
):
    mount_pip_conf_secret = (
        has_python_package_manager_conf_secret(extra_opts) if extra_opts else False
    )
    with TemporaryDirectory() as local_dir:
        docker_build_configuration = _convert_to_dockerfile_build_config(
            build_configuration,
            local_dir=local_dir,
            mount_pip_conf_secret=mount_pip_conf_secret,
        )
        dockerfile.build(
            tag=tag,
            build_configuration=docker_build_configuration,
            extra_opts=extra_opts,
        )
