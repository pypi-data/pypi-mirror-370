import atexit
import threading
import weakref
from typing import TYPE_CHECKING, Dict, Optional

from truefoundry.common.request_utils import urllib3_retry
from truefoundry.common.session import Session
from truefoundry.common.utils import (
    get_tfy_servers_config,
    get_user_agent,
    relogin_error_message,
)
from truefoundry.ml._autogen.client import (  # type: ignore[attr-defined]
    ApiClient,
    Configuration,
)
from truefoundry.ml.exceptions import MlFoundryException
from truefoundry.ml.logger import logger

if TYPE_CHECKING:
    from truefoundry.ml.mlfoundry_run import MlFoundryRun

SESSION_LOCK = threading.RLock()
ACTIVE_SESSION: Optional["MLFoundrySession"] = None


class ActiveRuns:
    def __init__(self):
        self._active_runs: Dict[str, weakref.ReferenceType["MlFoundryRun"]] = {}

    def add_run(self, run: "MlFoundryRun"):
        with SESSION_LOCK:
            self._active_runs[run.run_id] = weakref.ref(run)

    def remove_run(self, run: "MlFoundryRun"):
        with SESSION_LOCK:
            if run.run_id in self._active_runs:
                del self._active_runs[run.run_id]

    def close_active_runs(self):
        with SESSION_LOCK:
            for run_ref in list(self._active_runs.values()):
                run = run_ref()
                if run and run.auto_end:
                    run.end()
            self._active_runs.clear()


ACTIVE_RUNS = ActiveRuns()
atexit.register(ACTIVE_RUNS.close_active_runs)


class MLFoundrySession(Session):
    def _assert_not_closed(self):
        if self._closed:
            raise MlFoundryException(
                "This session has been deactivated.\n"
                "At a time only one `client` (received from "
                "`truefoundry.ml.get_client()` function call) can be used"
            )

    def close(self):
        global ACTIVE_RUNS
        logger.debug("Closing existing session")
        ACTIVE_RUNS.close_active_runs()
        super().close()

    @classmethod
    def new(cls) -> "MLFoundrySession":
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


class MLFoundryServerApiClient(ApiClient):
    def __init__(self, session: Optional[MLFoundrySession] = None, *args, **kwargs):
        self.session = session
        super().__init__(*args, **kwargs)

    @classmethod
    def from_session(cls, session: MLFoundrySession) -> "MLFoundryServerApiClient":
        mlfoundry_server_url = get_tfy_servers_config(
            session.tfy_host
        ).mlfoundry_server_url
        configuration = Configuration(
            host=mlfoundry_server_url.rstrip("/"),
            access_token=session.access_token,
        )
        configuration.retries = urllib3_retry(retries=2)
        api_client = cls(session=session, configuration=configuration)
        api_client.user_agent = get_user_agent()
        return api_client

    def _ensure_session(self):
        if self.session is None:
            raise MlFoundryException(
                relogin_error_message(
                    "No active session found. Perhaps you are not logged in?",
                )
            )

    @property
    def tfy_host(self) -> str:
        self._ensure_session()
        assert self.session is not None
        return self.session.tfy_host

    @property
    def access_token(self) -> str:
        self._ensure_session()
        assert self.session is not None
        return self.session.access_token


def _get_api_client(
    session: Optional[MLFoundrySession] = None,
    allow_anonymous: bool = False,
) -> MLFoundryServerApiClient:
    global ACTIVE_SESSION

    session = session or ACTIVE_SESSION
    if session is None:
        if allow_anonymous:
            return MLFoundryServerApiClient(session=None)
        else:
            raise MlFoundryException(
                relogin_error_message(
                    "No active session found. Perhaps you are not logged in?",
                )
            )
    return MLFoundryServerApiClient.from_session(session)
