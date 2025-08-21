import shlex
from typing import List, Optional

from truefoundry.common.constants import ENV_VARS
from truefoundry.deploy.builder.constants import (
    BUILDKIT_SECRET_MOUNT_PIP_CONF_ID,
    BUILDKIT_SECRET_MOUNT_UV_CONF_ID,
    PIP_CONF_SECRET_MOUNT_AS_ENV,
    UV_CONF_SECRET_MOUNT_AS_ENV,
)


def _get_id_from_buildkit_secret_value(value: str) -> Optional[str]:
    parts = value.split(",")
    secret_config = {}
    for part in parts:
        kv = part.split("=", 1)
        if len(kv) != 2:
            continue
        key, value = kv
        secret_config[key] = value

    if "id" in secret_config and "src" in secret_config:
        return secret_config["id"]

    return None


def has_python_package_manager_conf_secret(docker_build_extra_args: List[str]) -> bool:
    args = [arg.strip() for arg in docker_build_extra_args]
    for i, arg in enumerate(docker_build_extra_args):
        if (
            arg == "--secret"
            and i + 1 < len(args)
            and (
                _get_id_from_buildkit_secret_value(args[i + 1])
                in (BUILDKIT_SECRET_MOUNT_PIP_CONF_ID, BUILDKIT_SECRET_MOUNT_UV_CONF_ID)
            )
        ):
            return True
    return False


def generate_pip_install_command(
    requirements_path: Optional[str],
    pip_packages: Optional[List[str]],
    mount_pip_conf_secret: bool = False,
) -> Optional[str]:
    upgrade_pip_command = "python -m pip install -U pip setuptools wheel"
    envs = []
    if mount_pip_conf_secret:
        envs.append(PIP_CONF_SECRET_MOUNT_AS_ENV)

    command = ["python", "-m", "pip", "install", "--use-pep517", "--no-cache-dir"]
    args = []
    if requirements_path:
        args.append("-r")
        args.append(requirements_path)

    if pip_packages:
        args.extend(pip_packages)

    if not args:
        return None

    final_pip_install_command = shlex.join(envs + command + args)
    final_docker_run_command = " && ".join(
        [upgrade_pip_command, final_pip_install_command]
    )
    return final_docker_run_command


def generate_uv_pip_install_command(
    requirements_path: Optional[str],
    pip_packages: Optional[List[str]],
    mount_uv_conf_secret: bool = False,
) -> Optional[str]:
    upgrade_pip_command = "python -m pip install -U pip setuptools wheel"
    uv_mount = f"--mount=from={ENV_VARS.TFY_PYTHON_BUILD_UV_IMAGE_URI},source=/uv,target=/usr/local/bin/uv"
    envs = [
        "UV_LINK_MODE=copy",
        "UV_PYTHON_DOWNLOADS=never",
        "UV_INDEX_STRATEGY=unsafe-best-match",
    ]
    if mount_uv_conf_secret:
        envs.append(UV_CONF_SECRET_MOUNT_AS_ENV)

    command = ["uv", "pip", "install", "--no-cache-dir"]

    args = []

    if requirements_path:
        args.append("-r")
        args.append(requirements_path)

    if pip_packages:
        args.extend(pip_packages)

    if not args:
        return None

    uv_pip_install_command = shlex.join(envs + command + args)
    shell_commands = " && ".join([upgrade_pip_command, uv_pip_install_command])
    final_docker_run_command = " ".join([uv_mount, shell_commands])

    return final_docker_run_command


def generate_apt_install_command(apt_packages: Optional[List[str]]) -> Optional[str]:
    packages_list = None
    if apt_packages:
        packages_list = " ".join(p.strip() for p in apt_packages if p.strip())
    if not packages_list:
        return None
    apt_update_command = "apt update"
    apt_install_command = f"DEBIAN_FRONTEND=noninteractive apt install -y --no-install-recommends {packages_list}"
    clear_apt_lists_command = "rm -rf /var/lib/apt/lists/*"
    return " && ".join(
        [apt_update_command, apt_install_command, clear_apt_lists_command]
    )
