from __future__ import annotations

import functools
from typing import Callable, TypeVar

import requests
from packaging import version
from typing_extensions import ParamSpec

from truefoundry.common.constants import (
    SERVICEFOUNDRY_CLIENT_MAX_RETRIES,
    VERSION_PREFIX,
)
from truefoundry.common.entities import (
    PythonSDKConfig,
    TenantInfo,
)
from truefoundry.common.request_utils import (
    request_handling,
    requests_retry_session,
)
from truefoundry.common.utils import (
    get_tfy_servers_config,
    timed_lru_cache,
)
from truefoundry.logger import logger
from truefoundry.version import __version__

P = ParamSpec("P")
R = TypeVar("R")


def check_min_cli_version(fn: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(fn)
    def inner(*args: P.args, **kwargs: P.kwargs) -> R:
        client: "ServiceFoundryServiceClient" = args[0]
        client.check_min_cli_version()
        return fn(*args, **kwargs)

    return inner


def session_with_retries(
    retries: int = SERVICEFOUNDRY_CLIENT_MAX_RETRIES,
) -> requests.Session:
    return requests_retry_session(retries=retries)


@timed_lru_cache(seconds=30 * 60)
def _cached_get_tenant_info(api_server_url: str, tenant_host: str) -> TenantInfo:
    response = session_with_retries().get(
        url=f"{api_server_url}/{VERSION_PREFIX}/tenant-id",
        params={"hostName": tenant_host},
    )
    response_data = request_handling(response)
    return TenantInfo.parse_obj(response_data)


@timed_lru_cache(seconds=30 * 60)
def _cached_get_python_sdk_config(api_server_url: str) -> PythonSDKConfig:
    response = session_with_retries().get(
        url=f"{api_server_url}/{VERSION_PREFIX}/min-cli-version"
    )
    response_data = request_handling(response)
    return PythonSDKConfig.parse_obj(response_data)


class ServiceFoundryServiceClient:
    def __init__(self, tfy_host: str):
        self._tfy_host = tfy_host.strip("/")
        tfy_servers_config = get_tfy_servers_config(self._tfy_host)
        self._tenant_host = tfy_servers_config.tenant_host
        self._api_server_url = tfy_servers_config.servicefoundry_server_url

    @property
    def tfy_host(self) -> str:
        return self._tfy_host

    @property
    def tenant_info(self) -> TenantInfo:
        return _cached_get_tenant_info(
            self._api_server_url,
            tenant_host=self._tenant_host,
        )

    @property
    def python_sdk_config(self) -> PythonSDKConfig:
        return _cached_get_python_sdk_config(
            self._api_server_url,
        )

    @functools.cached_property
    def _min_cli_version_required(self) -> str:
        return self.python_sdk_config.truefoundry_cli_min_version

    def check_min_cli_version(self) -> None:
        if __version__ != "0.0.0":
            # "0.0.0" indicates dev version
            # noinspection PyProtectedMember
            min_cli_version_required = self._min_cli_version_required
            if version.parse(__version__) < version.parse(min_cli_version_required):
                raise Exception(
                    "You are using an outdated version of `truefoundry`.\n"
                    f"Run `pip install truefoundry>={min_cli_version_required}` to install the supported version.",
                )
        else:
            logger.debug("Ignoring minimum cli version check")
