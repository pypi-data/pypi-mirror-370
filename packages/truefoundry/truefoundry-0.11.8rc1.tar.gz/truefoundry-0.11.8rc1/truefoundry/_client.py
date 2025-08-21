import truefoundry_sdk
from truefoundry_sdk.core.client_wrapper import SyncClientWrapper

from truefoundry.common.session import Session


def _get_base_url(self: SyncClientWrapper) -> str:
    if not isinstance(self._base_url, str):
        self._base_url = self._base_url()
    return self._base_url


class _LazyTrueFoundry(truefoundry_sdk.TrueFoundry):
    def _get_session(self) -> Session:
        if self._session is None:
            self._session = Session.new()
        return self._session

    def __init__(self):
        self._session = None
        # We patch this because SyncClientWrapper.get_base_url is expected to return a string but
        # we need to ensure that the base_url is only resolved once any requests are made
        # Flow:
        # internal http client tries to resolve base_url
        #   -> SyncClientWrapper.get_base_url (_get_base_url)
        #     -> self._get_session().tfy_host   # where self._get_session itself caches the session instance
        SyncClientWrapper.get_base_url = _get_base_url
        super().__init__(
            # since our base_url resolving is tied to session creation, we pass a callable that
            # the above _get_base_url will replace with the resolved result
            base_url=lambda: self._get_session().tfy_host,  # type: ignore
            api_key=lambda: self._get_session().access_token,
        )


client = _LazyTrueFoundry()
