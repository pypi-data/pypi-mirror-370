from abc import ABC, abstractmethod
from typing import Any

from luna_quantum.client.interfaces.clients.info_rest_client_i import IInfoRestClient
from luna_quantum.client.interfaces.clients.model_rest_client_i import (
    IModelRestClient,
)
from luna_quantum.client.interfaces.clients.qpu_token_rest_client_i import (
    IQpuTokenRestClient,
)
from luna_quantum.client.interfaces.clients.solve_job_rest_client_i import (
    ISolveJobRestClient,
)
from luna_quantum.client.interfaces.services.service_i import IService


class ILunaSolve(IService, ABC):
    """Inteface for luna solve service."""

    @abstractmethod
    def __init__(self, api_key: str | None = None, *args: Any, **kwargs: Any) -> None:
        pass

    @property
    @abstractmethod
    def model(self) -> IModelRestClient:
        """
        Returns a model rest client.

        Returns
        -------
            IModelRestClient

        """
        raise NotImplementedError

    @property
    @abstractmethod
    def solve_job(self) -> ISolveJobRestClient:
        """
        Returns a solve job rest client.

        Returns
        -------
            ISolveJobRestClient

        """
        raise NotImplementedError

    @property
    @abstractmethod
    def qpu_token(self) -> IQpuTokenRestClient:
        """
        Returns a qpu token rest client.

        Returns
        -------
           IQpuTokenRestClient
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def info(self) -> IInfoRestClient:
        """
        Returns an info rest client.

        Returns
        -------
           IInfoRestClient
        """
        raise NotImplementedError
