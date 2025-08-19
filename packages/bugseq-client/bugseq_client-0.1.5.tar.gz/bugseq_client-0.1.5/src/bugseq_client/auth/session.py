import logging

from authlib.integrations.requests_client import OAuth2Session

from .storage import CredentialStorageProvider
from .web_auth import OAuthConfig, run_web_flow_for_token

logger = logging.getLogger(__name__)


class Session:
    def __init__(
        self,
        cfg: OAuthConfig,
        storage: CredentialStorageProvider,
    ):
        self.cfg = cfg
        self.storage = storage

        # if we don't have a valid refresh token, the user needs to re-auth
        existing_token = self._get_or_auth_token()

        self._session = OAuth2Session(
            self.cfg.client_id,
            self.cfg.client_secret,
            scope=self.cfg.scope,
            token=existing_token,
            token_endpoint=self.cfg.token_url,
            update_token=self._save_token,
        )

        self._session.ensure_active_token()

    def _save_token(self, token: dict, refresh_token: str | None = None):
        self.storage.store_token(self.cfg.app_name, token)

    def _get_or_auth_token(self) -> dict:
        """
        Return a token. If none is stored, run a local web flow to obtain one and
        persist it.
        """
        existing = self.storage.load_token(self.cfg.app_name)
        if existing:
            # there doesn't seem to be a way to know if this refresh token is expired
            # here.
            return existing

        logger.debug("no token found, initiating auth flow.")
        token = run_web_flow_for_token(self.cfg)
        self._save_token(token)
        return token

    def get_token(self) -> str:
        """
        Return a valid bearer token.
        """

        self._session.ensure_active_token()
        return self._session.token["access_token"]
