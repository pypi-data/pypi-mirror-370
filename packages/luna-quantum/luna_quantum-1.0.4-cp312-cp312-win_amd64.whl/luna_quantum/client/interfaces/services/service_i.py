from abc import ABC, abstractmethod

from httpx import Client


class IService(ABC):
    """Interface for luna services."""

    @property
    @abstractmethod
    def client(self) -> Client:
        """
        Return the httpx client.

        Returns
        -------
        Client
            A httpx client.
        """

    @classmethod
    @abstractmethod
    def authenticate(cls, api_key: str) -> None:
        """
        Authenticate the client with the given API key.

        Parameters
        ----------
        api_key : str
            The API key used to authenticate the client.

        Returns
        -------
        None
            This method does not return any value.
        """
