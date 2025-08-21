from mako.template import Template

from truefoundry.common.constants import ENV_VARS, PythonPackageManager
from truefoundry.deploy._autogen.models import SparkBuild
from truefoundry.deploy.builder.constants import (
    PIP_CONF_BUILDKIT_SECRET_MOUNT,
    UV_CONF_BUILDKIT_SECRET_MOUNT,
)
from truefoundry.deploy.builder.utils import (
    generate_pip_install_command,
    generate_uv_pip_install_command,
)
from truefoundry.deploy.v2.lib.patched_models import (
    _resolve_requirements_path,
)

# TODO (chiragjn): Switch to a non-root user inside the container

_POST_PYTHON_INSTALL_TEMPLATE = """
% if requirements_path is not None:
COPY ${requirements_path} ${requirements_destination_path}
% endif
% if python_packages_install_command is not None:
RUN ${package_manager_config_secret_mount} ${python_packages_install_command}
% endif
ENV PYTHONDONTWRITEBYTECODE=1
ENV IPYTHONDIR=/tmp/.ipython
USER 1001
COPY . /app
"""

_POST_USER_TEMPLATE = """
COPY tfy_execute_notebook.py /app/tfy_execute_notebook.py
"""

_ALMOND_INSTALL_TEMPLATE = """
ENV COURSIER_CACHE=/opt/coursier-cache
RUN install_packages curl
RUN curl -Lo coursier https://git.io/coursier-cli && \
    chmod +x coursier && \
    ./coursier launch almond:0.14.1 -- --install --global && \
    chown -R 1001:0 /usr/local/share/jupyter && \
    chown -R 1001:0 /opt/coursier-cache && \
    rm -f coursier
"""

# Docker image size with almond - 1.26GB
# Docker image size without almond - 1.1GB
# Not much harm in packaging almond by default
DOCKERFILE_TEMPLATE = Template(
    """
FROM ${spark_image_repo}:${spark_version}
USER root
RUN apt update && \
    DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*
"""
    + _ALMOND_INSTALL_TEMPLATE
    + _POST_PYTHON_INSTALL_TEMPLATE
    + _POST_USER_TEMPLATE
)

ADDITIONAL_PIP_PACKAGES = [
    "papermill>=2.6.0,<2.7.0",
    "ipykernel>=6.0.0,<7.0.0",
    "nbconvert>=7.16.6,<7.17.0",
    "boto3>=1.38.43,<1.40.0",
]


def generate_dockerfile_content(
    build_configuration: SparkBuild,
    package_manager: str = ENV_VARS.TFY_PYTHON_BUILD_PACKAGE_MANAGER,
    mount_python_package_manager_conf_secret: bool = False,
) -> str:
    # TODO (chiragjn): Handle recursive references to other requirements files e.g. `-r requirements-gpu.txt`
    requirements_path = _resolve_requirements_path(
        build_context_path=build_configuration.build_context_path,
        requirements_path=build_configuration.requirements_path,
    )
    requirements_destination_path = (
        "/tmp/requirements.txt" if requirements_path else None
    )
    if not build_configuration.spark_version:
        raise ValueError(
            "`spark_version` is required for `tfy-spark-buildpack` builder"
        )

    if package_manager == PythonPackageManager.PIP.value:
        python_packages_install_command = generate_pip_install_command(
            requirements_path=requirements_destination_path,
            pip_packages=ADDITIONAL_PIP_PACKAGES,
            mount_pip_conf_secret=mount_python_package_manager_conf_secret,
        )
    elif package_manager == PythonPackageManager.UV.value:
        python_packages_install_command = generate_uv_pip_install_command(
            requirements_path=requirements_destination_path,
            pip_packages=ADDITIONAL_PIP_PACKAGES,
            mount_uv_conf_secret=mount_python_package_manager_conf_secret,
        )
    else:
        raise ValueError(f"Unsupported package manager: {package_manager}")

    template_args = {
        "spark_image_repo": ENV_VARS.TFY_SPARK_BUILD_SPARK_IMAGE_REPO,
        "spark_version": build_configuration.spark_version,
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

    dockerfile_content = DOCKERFILE_TEMPLATE.render(**template_args)
    return dockerfile_content
