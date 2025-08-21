import time
from abc import ABC, abstractmethod
from typing import Optional

import requests

from truefoundry.common.constants import VERSION_PREFIX
from truefoundry.common.entities import DeviceCode, Token
from truefoundry.common.exceptions import BadRequestException
from truefoundry.common.request_utils import (
    request_handling,
    requests_retry_session,
)
from truefoundry.common.utils import poll_for_function, relogin_error_message
from truefoundry.logger import logger


class AuthServiceClient(ABC):
    def __init__(self, tenant_name: str):
        self._tenant_name = tenant_name

    @classmethod
    def from_tfy_host(cls, tfy_host: str) -> "AuthServiceClient":
        from truefoundry.common.servicefoundry_client import (
            ServiceFoundryServiceClient,
        )

        client = ServiceFoundryServiceClient(tfy_host=tfy_host)
        if client.python_sdk_config.use_sfy_server_auth_apis:
            return ServiceFoundryServerAuthServiceClient(
                tenant_name=client.tenant_info.tenant_name, url=client._api_server_url
            )
        return AuthServerServiceClient(
            tenant_name=client.tenant_info.tenant_name,
            url=client.tenant_info.auth_server_url,
        )

    @abstractmethod
    def refresh_token(self, token: Token, host: Optional[str] = None) -> Token: ...

    @abstractmethod
    def get_device_code(self) -> DeviceCode: ...

    @abstractmethod
    def get_token_from_device_code(
        self, device_code: str, timeout: float = 60, poll_interval_seconds: int = 1
    ) -> Token: ...


class ServiceFoundryServerAuthServiceClient(AuthServiceClient):
    def __init__(self, tenant_name: str, url: str):
        super().__init__(tenant_name=tenant_name)
        self._api_server_url = url

    def refresh_token(self, token: Token, host: Optional[str] = None) -> Token:
        host_arg_str = host if host else "HOST"
        if not token.refresh_token:
            # TODO: Add a way to propagate error messages without traceback to the output interface side
            raise Exception(
                relogin_error_message(
                    "Unable to resume login session.", host=host_arg_str
                )
            )
        url = f"{self._api_server_url}/{VERSION_PREFIX}/oauth2/token"
        data = {
            "tenantName": token.tenant_name,
            "refreshToken": token.refresh_token,
            "grantType": "refresh_token",
            "returnJWT": True,
        }
        session = requests_retry_session(retries=2)
        response = session.post(url, json=data)
        try:
            response_data = request_handling(response)
            return Token.parse_obj(response_data)
        except BadRequestException as ex:
            raise Exception(
                relogin_error_message(
                    "Unable to resume login session.", host=host_arg_str
                )
            ) from ex

    def get_device_code(self) -> DeviceCode:
        url = f"{self._api_server_url}/{VERSION_PREFIX}/oauth2/device-authorize"
        data = {"tenantName": self._tenant_name}
        session = requests_retry_session(retries=2)
        response = session.post(url, json=data)
        response_data = request_handling(response)
        return DeviceCode.parse_obj(response_data)

    def get_token_from_device_code(
        self, device_code: str, timeout: float = 60, poll_interval_seconds: int = 1
    ) -> Token:
        timeout = timeout or 60
        poll_interval_seconds = poll_interval_seconds or 1
        url = f"{self._api_server_url}/{VERSION_PREFIX}/oauth2/token"
        data = {
            "tenantName": self._tenant_name,
            "deviceCode": device_code,
            "grantType": "device_code",
            "returnJWT": True,
        }
        start_time = time.monotonic()

        for response in poll_for_function(
            requests.post, poll_after_secs=poll_interval_seconds, url=url, json=data
        ):
            if response.status_code == 201:
                response = response.json()
                return Token.parse_obj(response)
            elif response.status_code == 202:
                logger.debug("User has not authorized yet. Checking again.")
            else:
                raise Exception(
                    "Failed to get token using device code. "
                    f"status_code {response.status_code},\n {response.text}"
                )
            time_elapsed = time.monotonic() - start_time
            if time_elapsed > timeout:
                logger.warning("Polled server for %s secs.", int(time_elapsed))
                break

        raise Exception(f"Did not get authorized within {timeout} seconds.")


class AuthServerServiceClient(AuthServiceClient):
    def __init__(self, tenant_name: str, url: str):
        super().__init__(tenant_name=tenant_name)

        self._auth_server_url = url

    def refresh_token(self, token: Token, host: Optional[str] = None) -> Token:
        host_arg_str = host if host else "HOST"
        if not token.refresh_token:
            # TODO: Add a way to propagate error messages without traceback to the output interface side
            raise Exception(
                relogin_error_message(
                    "Unable to resume login session.", host=host_arg_str
                )
            )
        url = f"{self._auth_server_url}/api/{VERSION_PREFIX}/oauth/token/refresh"
        data = {
            "tenantName": token.tenant_name,
            "refreshToken": token.refresh_token,
        }
        session = requests_retry_session(retries=2)
        response = session.post(url, json=data)
        try:
            response_data = request_handling(response)
            return Token.parse_obj(response_data)
        except BadRequestException as ex:
            raise Exception(
                relogin_error_message(
                    "Unable to resume login session.", host=host_arg_str
                )
            ) from ex

    def get_device_code(self) -> DeviceCode:
        url = f"{self._auth_server_url}/api/{VERSION_PREFIX}/oauth/device"
        data = {"tenantName": self._tenant_name}
        session = requests_retry_session(retries=2)
        response = session.post(url, json=data)
        response_data = request_handling(response)
        assert isinstance(response_data, dict)
        # TODO: temporary cleanup of incorrect attributes
        return DeviceCode.parse_obj(
            {
                "userCode": response_data.get("userCode"),
                "deviceCode": response_data.get("deviceCode"),
            }
        )

    def get_token_from_device_code(
        self, device_code: str, timeout: float = 60, poll_interval_seconds: int = 1
    ) -> Token:
        timeout = timeout or 60
        poll_interval_seconds = poll_interval_seconds or 1
        url = f"{self._auth_server_url}/api/{VERSION_PREFIX}/oauth/device/token"
        data = {
            "tenantName": self._tenant_name,
            "deviceCode": device_code,
        }
        start_time = time.monotonic()

        for response in poll_for_function(
            requests.post, poll_after_secs=poll_interval_seconds, url=url, json=data
        ):
            if response.status_code == 201:
                response = response.json()
                return Token.parse_obj(response)
            elif response.status_code == 202:
                logger.debug("User has not authorized yet. Checking again.")
            else:
                raise Exception(
                    "Failed to get token using device code. "
                    f"status_code {response.status_code},\n {response.text}"
                )
            time_elapsed = time.monotonic() - start_time
            if time_elapsed > timeout:
                logger.warning("Polled server for %s secs.", int(time_elapsed))
                break

        raise Exception(f"Did not get authorized within {timeout} seconds.")
