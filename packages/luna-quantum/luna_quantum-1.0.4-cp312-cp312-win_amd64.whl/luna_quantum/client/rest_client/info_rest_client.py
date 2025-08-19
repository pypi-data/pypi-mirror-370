from __future__ import annotations

from typing import Any

from luna_quantum.client.interfaces.clients.info_rest_client_i import IInfoRestClient
from luna_quantum.client.schemas.solver_info import SolverInfo


class InfoRestClient(IInfoRestClient):
    """Implementation of the info rest client."""

    _endpoint = "/"

    _endpoint_solvers = "/solvers"
    _endpoint_providers = "/providers"

    def solvers_available(
        self, solver_name: str | None = None, **kwargs: Any
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
        params = {}
        if solver_name:
            params["solver_name"] = solver_name

        response = self._client.get(
            f"{self._endpoint_solvers}/available", params=params, **kwargs
        )

        response.raise_for_status()

        json: dict[str, dict[str, Any]] = response.json()
        to_return: dict[str, dict[str, SolverInfo]] = {}
        for provider, solvers in json.items():
            to_return[provider] = {}
            for solver in solvers:
                to_return[provider][solver] = SolverInfo.model_validate(
                    json[provider][solver]
                )

        return to_return

    def providers_available(self, **kwargs: Any) -> list[str]:
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
        response = self._client.get(f"{self._endpoint_providers}/available", **kwargs)

        response.raise_for_status()

        return list(response.json())
