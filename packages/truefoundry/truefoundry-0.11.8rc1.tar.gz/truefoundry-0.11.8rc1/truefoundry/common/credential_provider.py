import os
import threading
from abc import ABC, abstractmethod

from truefoundry.common.auth_service_client import AuthServiceClient
from truefoundry.common.constants import ENV_VARS, TFY_API_KEY_ENV_KEY
from truefoundry.common.credential_file_manager import CredentialsFileManager
from truefoundry.common.entities import CredentialsFileContent, Token
from truefoundry.common.utils import resolve_tfy_host
from truefoundry.logger import logger

TOKEN_REFRESH_LOCK = threading.RLock()


class CredentialProvider(ABC):
    @property
    @abstractmethod
    def token(self) -> Token: ...

    @property
    @abstractmethod
    def tfy_host(self) -> str: ...

    @staticmethod
    @abstractmethod
    def can_provide() -> bool: ...


class EnvCredentialProvider(CredentialProvider):
    def __init__(self) -> None:
        logger.debug("Using env var credential provider")
        api_key = (
            ENV_VARS.TFY_API_KEY.get_secret_value() if ENV_VARS.TFY_API_KEY else None
        )
        if not api_key:
            raise Exception(
                f"Value of {TFY_API_KEY_ENV_KEY} env var should be non-empty string"
            )
        self._host = resolve_tfy_host()
        self._auth_service = AuthServiceClient.from_tfy_host(tfy_host=self._host)
        self._token: Token = Token(access_token=api_key, refresh_token=None)

    @staticmethod
    def can_provide() -> bool:
        return TFY_API_KEY_ENV_KEY in os.environ

    @property
    def token(self) -> Token:
        with TOKEN_REFRESH_LOCK:
            if self._token.is_going_to_be_expired():
                logger.info("Refreshing access token")
                self._token = self._auth_service.refresh_token(
                    self._token, self.tfy_host
                )
            return self._token

    @property
    def tfy_host(self) -> str:
        return self._host


class FileCredentialProvider(CredentialProvider):
    def __init__(self) -> None:
        logger.debug("Using file credential provider")
        self._cred_file = CredentialsFileManager()

        with self._cred_file:
            self._last_cred_file_content = self._cred_file.read()
            self._token = self._last_cred_file_content.to_token()
            self._host = self._last_cred_file_content.host

        self._auth_service = AuthServiceClient.from_tfy_host(tfy_host=self._host)

    @staticmethod
    def can_provide() -> bool:
        with CredentialsFileManager() as cred_file:
            return cred_file.exists()

    @property
    def token(self) -> Token:
        with TOKEN_REFRESH_LOCK:
            if not self._token.is_going_to_be_expired():
                return self._token

            logger.info("Refreshing access token")
            with self._cred_file:
                new_cred_file_content = self._cred_file.read()
                new_token = new_cred_file_content.to_token()
                new_host = new_cred_file_content.host

                if new_cred_file_content == self._last_cred_file_content:
                    self._token = self._auth_service.refresh_token(
                        self._token, self.tfy_host
                    )
                    self._last_cred_file_content = CredentialsFileContent(
                        host=self._host,
                        access_token=self._token.access_token,
                        refresh_token=self._token.refresh_token,
                    )
                    self._cred_file.write(self._last_cred_file_content)
                    return self._token

                if (
                    new_host == self._host
                    and new_token.to_user_info() == self._token.to_user_info()
                ):
                    self._last_cred_file_content = new_cred_file_content
                    self._token = new_token
                    # recursive
                    return self.token

                raise Exception(
                    "Credentials on disk changed while truefoundry was running."
                )

    @property
    def tfy_host(self) -> str:
        return self._host
