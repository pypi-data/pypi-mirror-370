from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from luna_quantum.client.interfaces.clients.rest_client_i import IRestClient

if TYPE_CHECKING:
    from luna_quantum.client.schemas.solver_info import SolverInfo


class IInfoRestClient(IRestClient, ABC):
    """Interface of the info rest client."""

    @abstractmethod
    def solvers_available(
        self, solver_name: str | None = None, **kwargs: dict[str, Any]
    ) -> dict[str, dict[str, SolverInfo]]:
        """
        Get list of available solvers.

        Parameters
        ----------
        solver_name: Optional[str]
            Name of the solver that should be retrieved. If not specified, all solvers
            will be returned.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        Dict[str, Dict[str, SolverInfo]]
            Dictionary containing the provider name as the key, and a dictionary of
            the solver name and solver-specific information as the value.
        """
        raise NotImplementedError

    @abstractmethod
    def providers_available(self, **kwargs: dict[str, Any]) -> list[str]:
        """
        Get list of available providers.

        Parameters
        ----------
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        List[str]
            List of available QPU providers.
        """
        raise NotImplementedError
