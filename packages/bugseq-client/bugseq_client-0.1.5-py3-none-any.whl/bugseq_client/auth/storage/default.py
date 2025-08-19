import os

from .abstract import CredentialStorageProvider
from .keyring import CredentialStorageProviderKeyring
from .local import CredentialStorageProviderLocal


def get_default_credential_storage_provider() -> CredentialStorageProvider:
    """
    Determines which storage provider to use based on environment variables and
    availability.
    """
    env_name = "BUGSEQ_CREDENTIAL_STORAGE"
    env_val = os.getenv(env_name)

    if env_val == "keyring":
        return CredentialStorageProviderKeyring()
    if env_val == "file":
        return CredentialStorageProviderLocal()

    # Auto-detect
    for provider in [
        CredentialStorageProviderKeyring,
        CredentialStorageProviderLocal,
    ]:
        if provider.is_available():
            return provider()

    raise RuntimeError("No available storage providers found")
