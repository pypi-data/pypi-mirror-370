from abc import ABC, abstractmethod

from luna_quantum.client.interfaces.clients import ICircuitRestClient
from luna_quantum.client.interfaces.clients.qpu_token_rest_client_i import (
    IQpuTokenRestClient,
)
from luna_quantum.client.interfaces.services.service_i import IService


class ILunaQ(IService, ABC):
    """Interface for the LunaQ client."""

    @property
    @abstractmethod
    def qpu_token(self) -> IQpuTokenRestClient:
        """
        Returns a QPU token repository.

        Examples
        --------
            >>> add(4.0, 2.0)
            6.0
            >>> add(4, 2)
            6.0


        """
        raise NotImplementedError

    @property
    @abstractmethod
    def circuit(self) -> ICircuitRestClient:
        """Returns a circuit :py:class: repository."""
        raise NotImplementedError
