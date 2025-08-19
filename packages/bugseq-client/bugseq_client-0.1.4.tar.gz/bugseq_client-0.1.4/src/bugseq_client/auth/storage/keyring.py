import json
import logging

import keyring

from .abstract import CredentialStorageProvider

logger = logging.getLogger(__name__)


class CredentialStorageProviderKeyring(CredentialStorageProvider):
    """
    Stores credentials in the system keychain.
    """

    _version = 0

    def __init__(self):
        if not self.is_available():
            raise RuntimeError("Keyring is not available on this system.")

    @staticmethod
    def is_available() -> bool:
        try:
            kr = keyring.get_keyring()

            # run a quick test against the keyring
            # None --> fine - the keyring is accessible
            # Error --> the keyring is not accessible
            kr.get_password("bugseq-test", "bugseq-test")
            return True
        except keyring.errors.NoKeyringError:
            return False

    def _keyring_ids(self, app_name: str) -> tuple[str, str]:
        return (f"{app_name}.oauth2", "token")

    def store_token(self, app_name: str, token: dict) -> None:
        service, user = self._keyring_ids(app_name)
        logger.debug("storing credentials in keychain")

        token_contents = {"version": self._version, "token": token}

        keyring.set_password(service, user, json.dumps(token_contents))
        logger.debug("stored credentials in keychain")

    def load_token(self, app_name: str) -> dict | None:
        service, user = self._keyring_ids(app_name)

        logger.debug("loading credentials from keychain")
        token = keyring.get_password(service, user)
        if token:
            parsed = json.loads(token)
            if parsed["version"] != self._version:
                return None

            logger.debug("loaded credentials from keychain")
            return parsed["token"]

        return None
