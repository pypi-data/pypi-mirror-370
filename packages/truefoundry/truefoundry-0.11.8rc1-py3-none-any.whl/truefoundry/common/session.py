from __future__ import annotations

import threading
from typing import Optional

from truefoundry.common.credential_provider import (
    CredentialProvider,
    EnvCredentialProvider,
    FileCredentialProvider,
)
from truefoundry.common.entities import Token, UserInfo
from truefoundry.common.utils import relogin_error_message
from truefoundry.logger import logger

SESSION_LOCK = threading.RLock()
ACTIVE_SESSION: Optional["Session"] = None


class Session:
    def __init__(self) -> None:
        self._closed = False
        self._cred_provider: Optional[CredentialProvider] = self._get_cred_provider()
        self._user_info: Optional[UserInfo] = self.token.to_user_info()

    @staticmethod
    def _get_cred_provider() -> CredentialProvider:
        final_cred_provider = None
        for cred_provider in [EnvCredentialProvider, FileCredentialProvider]:
            if cred_provider.can_provide():
                final_cred_provider = cred_provider()
                break
        if final_cred_provider is None:
            raise Exception(
                relogin_error_message(
                    "No active session found. Perhaps you are not logged in?",
                )
            )
        return final_cred_provider

    @classmethod
    def new(cls) -> "Session":
        global ACTIVE_SESSION
        with SESSION_LOCK:
            new_session = cls()
            if ACTIVE_SESSION and ACTIVE_SESSION == new_session:
                return ACTIVE_SESSION

            if ACTIVE_SESSION:
                ACTIVE_SESSION.close()

            ACTIVE_SESSION = new_session
            logger.info(
                "Logged in to %r as %r",
                new_session.tfy_host,
                new_session.user_info.user_id,
            )

            return ACTIVE_SESSION

    def close(self):
        self._closed = True
        self._user_info = None
        self._cred_provider = None

    def _assert_not_closed(self):
        if self._closed:
            raise Exception("This session has been deactivated.")

    @property
    def access_token(self) -> str:
        assert self._cred_provider is not None
        return self.token.access_token

    @property
    def token(self) -> Token:
        assert self._cred_provider is not None
        return self._cred_provider.token

    @property
    def tfy_host(self) -> str:
        assert self._cred_provider is not None
        return self._cred_provider.tfy_host

    @property
    def user_info(self) -> UserInfo:
        self._assert_not_closed()
        assert self._user_info is not None
        return self._user_info

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Session):
            return False
        return (
            type(self._cred_provider) == type(other._cred_provider)  # noqa: E721
            and self.user_info == other.user_info
            and self.tfy_host == other.tfy_host
        )
