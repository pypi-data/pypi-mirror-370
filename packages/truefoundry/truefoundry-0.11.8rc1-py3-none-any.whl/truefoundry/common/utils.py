import json
import logging
import os
import platform
import sys
import time
from collections import namedtuple
from functools import lru_cache, wraps
from shutil import rmtree
from subprocess import check_output
from time import monotonic_ns
from typing import Callable, Generator, List, Optional, TypeVar
from urllib.parse import urljoin, urlparse

from truefoundry.common.constants import (
    API_SERVER_RELATIVE_PATH,
    ENV_VARS,
    MLFOUNDRY_SERVER_RELATIVE_PATH,
    TFY_API_KEY_ENV_KEY,
    TFY_DEBUG_ENV_KEY,
    TFY_HOST_ENV_KEY,
    TFY_INTERNAL_ENV_KEY,
)
from truefoundry.pydantic_v1 import BaseSettings
from truefoundry.version import __version__

logger = logging.getLogger(__name__)

T = TypeVar("T")
InstalledPipPackage = namedtuple("InstalledPipPackage", ["name", "version"])


class _TFYServersConfig(BaseSettings):
    class Config:
        env_prefix = "TFY_CLI_LOCAL_"
        env_file = ".tfy-cli-local.env"

    tenant_host: str
    servicefoundry_server_url: str
    mlfoundry_server_url: str

    @classmethod
    def from_tfy_host(cls, tfy_host: str) -> "_TFYServersConfig":
        tfy_host = tfy_host.strip("/")
        return cls(
            tenant_host=urlparse(tfy_host).netloc,
            servicefoundry_server_url=urljoin(tfy_host, API_SERVER_RELATIVE_PATH),
            mlfoundry_server_url=urljoin(tfy_host, MLFOUNDRY_SERVER_RELATIVE_PATH),
        )


_tfy_servers_config = None


def get_tfy_servers_config(tfy_host: str) -> _TFYServersConfig:
    global _tfy_servers_config
    if _tfy_servers_config is None:
        if ENV_VARS.TFY_CLI_LOCAL_DEV_MODE:
            _tfy_servers_config = _TFYServersConfig()
        else:
            _tfy_servers_config = _TFYServersConfig.from_tfy_host(tfy_host)
    return _tfy_servers_config


def relogin_error_message(message: str, host: str = "HOST") -> str:
    suffix = ""
    if host == "HOST":
        suffix = " where HOST is TrueFoundry platform URL"
    return (
        f"{message}\n"
        f"To relogin, use `tfy login --host {host} --relogin` "
        f"or `truefoundry.login(host={host!r}, relogin=True)` function" + suffix
    )


def timed_lru_cache(
    seconds: int = 300, maxsize: Optional[int] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    def wrapper_cache(func: Callable[..., T]) -> Callable[..., T]:
        func = lru_cache(maxsize=maxsize)(func)
        func.delta = seconds * 10**9
        func.expiration = monotonic_ns() + func.delta

        @wraps(func)
        def wrapped_func(*args, **kwargs):
            if monotonic_ns() >= func.expiration:
                func.cache_clear()
                func.expiration = monotonic_ns() + func.delta
            return func(*args, **kwargs)

        return wrapped_func

    return wrapper_cache


def poll_for_function(
    func: Callable[..., T],
    poll_after_secs: int = 5,
    *args,
    **kwargs,
) -> Generator[T, None, None]:
    while True:
        yield func(*args, **kwargs)
        time.sleep(poll_after_secs)


def validate_tfy_host(tfy_host: str) -> None:
    if not (tfy_host.startswith("https://") or tfy_host.startswith("http://")):
        raise ValueError(
            f"Invalid host {tfy_host!r}. It should start with https:// or http://"
        )


def resolve_tfy_host(tfy_host: Optional[str] = None) -> str:
    tfy_host = tfy_host or ENV_VARS.TFY_HOST
    if not tfy_host:
        if ENV_VARS.TFY_API_KEY:
            raise ValueError(
                f"TFY_HOST` env must be set since `{TFY_API_KEY_ENV_KEY}` env is set. Either set `{TFY_HOST_ENV_KEY}` or unset `{TFY_API_KEY_ENV_KEY}` and login"
            )
        else:
            raise ValueError(
                f"Either `host` should be provided using `--host <value>`, or `{TFY_HOST_ENV_KEY}` env must be set"
            )
    tfy_host = tfy_host.strip("/")
    validate_tfy_host(tfy_host)
    return tfy_host


class ContextualDirectoryManager:
    def __init__(self, dir_path: str, cleanup_on_error: bool = True):
        self.dir_path = dir_path
        self.cleanup_on_error = cleanup_on_error

    def __enter__(self):
        if os.path.exists(self.dir_path):
            raise FileExistsError(
                f"The directory {self.dir_path!r} already exists. "
                "Please provide a path with a different name that does not already exist."
            )

        os.makedirs(self.dir_path, exist_ok=False)
        return self.dir_path

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cleanup_on_error and exc_type is not None:
            # Only delete the directory if an exception occurred
            if os.path.exists(self.dir_path):
                rmtree(self.dir_path)


def get_python_version_major_minor() -> str:
    """
    Returns the major.minor version of the Python interpreter
    """
    version_info = sys.version_info
    return f"{version_info.major}.{version_info.minor}"


def list_pip_packages_installed(
    filter_package_names: Optional[List[str]] = None,
) -> List[InstalledPipPackage]:
    """
    List the installed package_names, along with their versions.
    Args:
        filter_package_names (List[str]): A list of specific libraries to filter for.

    Returns:
        List[InstalledPipPackage]: A list of InstalledPipPackage namedtuples for each match.
    """
    relevant_package_names: List[InstalledPipPackage] = []

    # Get the installed packages in JSON format from pip
    try:
        output = check_output(
            [
                sys.executable,
                "-m",
                "pip",
                "--disable-pip-version-check",
                "list",
                "--pre",
                "--format=json",
            ]
        )
        installed_package_names = json.loads(output.decode("utf-8"))
    except Exception:
        logger.exception("Failed to list installed packages using pip.")
        return relevant_package_names

    package_names_to_check = set(filter_package_names or [])
    for package in installed_package_names:
        if package["name"] in package_names_to_check:
            relevant_package_names.append(
                InstalledPipPackage(package["name"], package["version"])
            )
    return relevant_package_names


def is_debug_env_set() -> bool:
    return (os.getenv(TFY_DEBUG_ENV_KEY) or "").lower() in ["true", "1"]


def is_internal_env_set() -> bool:
    return (os.getenv(TFY_INTERNAL_ENV_KEY) or "").lower() in ["true", "1"]


def get_user_agent() -> str:
    try:
        return f"truefoundry/{__version__} Python/{platform.python_version()} OS/{platform.system()}-{platform.release()} ({platform.architecture()[0]})"
    except Exception:
        return f"truefoundry/{__version__}"
