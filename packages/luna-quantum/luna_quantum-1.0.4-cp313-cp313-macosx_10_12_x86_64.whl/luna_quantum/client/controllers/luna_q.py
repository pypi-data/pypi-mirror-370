from __future__ import annotations

from typing import TYPE_CHECKING

from luna_quantum.client.controllers.luna_platform_client import (
    LunaPlatformClient,
    LunaPrefixEnum,
)
from luna_quantum.client.interfaces.services.luna_q_i import ILunaQ
from luna_quantum.client.rest_client import CircuitRestClient, QpuTokenRestClient

if TYPE_CHECKING:
    from luna_quantum.client.interfaces.clients import ICircuitRestClient
    from luna_quantum.client.interfaces.clients.qpu_token_rest_client_i import (
        IQpuTokenRestClient,
    )


class LunaQ(LunaPlatformClient, ILunaQ):
    """Implementation of LunaQ service."""

    qpu_token: IQpuTokenRestClient = None  # type: ignore[assignment]
    circuit: ICircuitRestClient = None  # type: ignore[assignment]

    def __init__(
        self, api_key: str | None = None, timeout: float | None = 240.0
    ) -> None:
        """
        LunaQ is the main entrypoint for all LunaQ related tasks.

        Parameters
        ----------
        api_key: str
            User's API key
        timeout: float
            Default timeout in seconds for the requests via the LunaQ client. `None`
            means that the SDK uses no timeouts. Note that either way the Luna platform
            itself will time out after 240 seconds.
            Default: 240.0
        """
        super().__init__(api_key=api_key, api=LunaPrefixEnum.LUNA_Q, timeout=timeout)

        self.circuit = CircuitRestClient(self)
        self.qpu_token = QpuTokenRestClient(self)

    @classmethod
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
        cls(api_key=api_key)
        cls._api_key = api_key
