import json
import logging
import os
from pathlib import Path

from .abstract import CredentialStorageProvider

logger = logging.getLogger(__name__)


class CredentialStorageProviderLocal(CredentialStorageProvider):
    """
    Stores credentials in a local file.
    """

    _version = 0

    @staticmethod
    def is_available():
        return True

    def _make_and_get_app_config_dir(self, app_name: str) -> Path:
        xdg_config_home_env = os.getenv("XDG_CONFIG_HOME")
        if xdg_config_home_env:
            xdg_config_home = Path(xdg_config_home_env)
        else:
            xdg_config_home = Path.home() / ".config"
        path = xdg_config_home / app_name.lower()
        path.mkdir(exist_ok=True, parents=True)
        return path

    def _cred_file_path(self, app_name: str) -> Path:
        return self._make_and_get_app_config_dir(app_name) / "credentials.json"

    def store_token(self, app_name: str, token: dict) -> None:
        logger.debug("storing credentials in config directory")

        token_contents = {"version": self._version, "token": token}
        self._write_token_file(app_name, json.dumps(token_contents))
        logger.debug("stored credentials in config directory")

    def load_token(self, app_name: str) -> dict | None:
        logger.debug("loading credentials from config directory")
        token = self._read_token_file(app_name)
        if token:
            parsed = json.loads(token)
            if parsed["version"] != self._version:
                return None

            logger.debug("loaded credentials from config directory")
            return parsed["token"]

        return None

    def _write_token_file(self, app_name: str, token: str) -> None:
        path = self._cred_file_path(app_name)
        # Restrict file permissions (0600 on POSIX)
        flags = os.O_WRONLY | os.O_CREAT | os.O_TRUNC
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW  # best effort
        fd = os.open(path, flags, 0o600)
        with os.fdopen(fd, "w") as f:
            f.write(token)

    def _read_token_file(self, app_name: str) -> str | None:
        path = self._cred_file_path(app_name)
        if not path.exists():
            return None
        try:
            return path.read_text()
        except Exception:
            return None
