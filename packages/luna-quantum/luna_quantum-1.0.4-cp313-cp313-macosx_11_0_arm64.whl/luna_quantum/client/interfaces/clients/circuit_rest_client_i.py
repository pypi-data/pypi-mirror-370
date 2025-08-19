from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from luna_quantum.client.interfaces.clients.rest_client_i import IRestClient

if TYPE_CHECKING:
    from luna_quantum.client.schemas.circuit import CircuitJob, CircuitResult
    from luna_quantum.client.schemas.enums.circuit import CircuitProviderEnum
    from luna_quantum.client.schemas.qpu_token.qpu_token import TokenProvider


class ICircuitRestClient(IRestClient, ABC):
    """Interface for circuit rest client."""

    @abstractmethod
    def create(
        self,
        circuit: str,
        provider: CircuitProviderEnum,
        params: dict[str, Any] | None = None,
        qpu_tokens: TokenProvider | None = None,
        **kwargs: Any,
    ) -> CircuitJob:
        """
        Create a circuit solution.

        Parameters
        ----------
        circuit: str
            The circuit which to create a solution for.
        provider: CircuitProviderEnum
            Which provider to use to solve the circuit.
        params: Dict[str, Any]
            Additional parameters of the circuit.
        qpu_tokens: Optional[TokenProvider]
            The tokens to be used for the QPU.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        CircuitJob
            The created circuit job.
        """
        raise NotImplementedError

    @abstractmethod
    def get(
        self,
        job: CircuitJob,
        **kwargs: Any,
    ) -> CircuitResult:
        """
        Get the result of a circuit.

        Parameters
        ----------
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        CircuitResult
            The result of solving the circuit.
        """
        raise NotImplementedError
