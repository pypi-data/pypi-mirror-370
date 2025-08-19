from abc import ABC, abstractmethod


class CredentialStorageProvider(ABC):
    """
    Abstract base class for credential storage providers.
    """

    @staticmethod
    @abstractmethod
    def is_available() -> bool:
        """
        Checks if the provider is available.
        """

    @abstractmethod
    def store_token(self, app_name: str, token: dict) -> None:
        """
        Stores the token.
        """
        pass

    @abstractmethod
    def load_token(self, app_name: str) -> dict | None:
        """
        Loads the token.
        """
        pass
