from mako.template import Template

from truefoundry.common.constants import ENV_VARS, PythonPackageManager
from truefoundry.deploy._autogen.models import TaskPySparkBuild
from truefoundry.deploy.builder.constants import (
    PIP_CONF_BUILDKIT_SECRET_MOUNT,
    UV_CONF_BUILDKIT_SECRET_MOUNT,
)
from truefoundry.deploy.builder.utils import (
    generate_apt_install_command,
    generate_pip_install_command,
    generate_uv_pip_install_command,
)
from truefoundry.deploy.v2.lib.patched_models import (
    _resolve_requirements_path,
)

# TODO[GW]: Switch to a non-root user inside the container
_POST_PYTHON_INSTALL_TEMPLATE = """
% if apt_install_command is not None:
RUN ${apt_install_command}
% endif
% if requirements_path is not None:
COPY ${requirements_path} ${requirements_destination_path}
% endif
% if python_packages_install_command is not None:
RUN ${package_manager_config_secret_mount} ${python_packages_install_command}
% endif
COPY . /app
WORKDIR /app
"""

# TODO[GW]: Check if the entrypoint for the image needs to change
# Using /opt/venv/ because flyte seems to be using it and this doesn't look configurable
# TODO[GW]: Double check this^
DOCKERFILE_TEMPLATE = Template(
    """
FROM ${spark_image_repo}:${spark_version}
ENV PATH=/opt/venv/bin:$PATH
USER root
RUN mkdir -p /var/lib/apt/lists/partial && \
    apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends git && \
    python -m venv /opt/venv/ && \
    rm -rf /var/lib/apt/lists/*
"""
    + _POST_PYTHON_INSTALL_TEMPLATE
)


def get_additional_pip_packages(build_configuration: TaskPySparkBuild):
    return [
        f"pyspark=={build_configuration.spark_version}",
    ]


def generate_dockerfile_content(
    build_configuration: TaskPySparkBuild,
    package_manager: str = ENV_VARS.TFY_PYTHON_BUILD_PACKAGE_MANAGER,
    mount_python_package_manager_conf_secret: bool = False,
) -> str:
    # TODO (chiragjn): Handle recursive references to other requirements files e.g. `-r requirements-gpu.txt`
    requirements_path = _resolve_requirements_path(
        build_context_path="",
        requirements_path=build_configuration.requirements_path,
    )
    requirements_destination_path = (
        "/tmp/requirements.txt" if requirements_path else None
    )
    # if not build_configuration.python_version:
    #     raise ValueError(
    #         "`python_version` is required for `tfy-python-buildpack` builder"
    #     )
    pip_packages = get_additional_pip_packages(build_configuration) + (
        build_configuration.pip_packages or []
    )
    if package_manager == PythonPackageManager.PIP.value:
        python_packages_install_command = generate_pip_install_command(
            requirements_path=requirements_destination_path,
            pip_packages=pip_packages,
            mount_pip_conf_secret=mount_python_package_manager_conf_secret,
        )
    elif package_manager == PythonPackageManager.UV.value:
        python_packages_install_command = generate_uv_pip_install_command(
            requirements_path=requirements_destination_path,
            pip_packages=pip_packages,
            mount_uv_conf_secret=mount_python_package_manager_conf_secret,
        )
    else:
        raise ValueError(f"Unsupported package manager: {package_manager}")

    apt_install_command = generate_apt_install_command(
        apt_packages=build_configuration.apt_packages
    )
    template_args = {
        "spark_image_repo": ENV_VARS.TFY_TASK_PYSPARK_BUILD_SPARK_IMAGE_REPO,
        "spark_version": build_configuration.spark_version,
        "apt_install_command": apt_install_command,
        "requirements_path": requirements_path,
        "requirements_destination_path": requirements_destination_path,
        "python_packages_install_command": python_packages_install_command,
    }

    if mount_python_package_manager_conf_secret:
        if package_manager == PythonPackageManager.PIP.value:
            template_args["package_manager_config_secret_mount"] = (
                PIP_CONF_BUILDKIT_SECRET_MOUNT
            )
        elif package_manager == PythonPackageManager.UV.value:
            template_args["package_manager_config_secret_mount"] = (
                UV_CONF_BUILDKIT_SECRET_MOUNT
            )
        else:
            raise ValueError(f"Unsupported package manager: {package_manager}")
    else:
        template_args["package_manager_config_secret_mount"] = ""

    template = DOCKERFILE_TEMPLATE

    dockerfile_content = template.render(**template_args)
    return dockerfile_content
