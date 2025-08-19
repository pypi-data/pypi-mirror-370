from __future__ import annotations

from typing import TYPE_CHECKING

from luna_quantum.client.controllers.luna_platform_client import (
    LunaPlatformClient,
    LunaPrefixEnum,
)
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.client.rest_client.info_rest_client import InfoRestClient
from luna_quantum.client.rest_client.model_rest_client import (
    ModelRestClient,
)
from luna_quantum.client.rest_client.qpu_token_rest_client import QpuTokenRestClient
from luna_quantum.client.rest_client.solve_job_rest_client import SolveJobRestClient

if TYPE_CHECKING:
    from luna_quantum.client.interfaces.clients import ISolveJobRestClient
    from luna_quantum.client.interfaces.clients.info_rest_client_i import (
        IInfoRestClient,
    )
    from luna_quantum.client.interfaces.clients.model_rest_client_i import (
        IModelRestClient,
    )
    from luna_quantum.client.interfaces.clients.qpu_token_rest_client_i import (
        IQpuTokenRestClient,
    )


class LunaSolve(LunaPlatformClient, ILunaSolve):
    """Implementation of LunaSolve service."""

    _model: IModelRestClient
    _solve_job: ISolveJobRestClient
    _qpu_token: IQpuTokenRestClient
    _info: IInfoRestClient

    def __init__(
        self, api_key: str | None = None, timeout: float | None = 240.0
    ) -> None:
        """
        LunaSolve is the main entrypoint for all LunaSolve related tasks.

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
        super().__init__(
            api_key=api_key,
            api=LunaPrefixEnum.LUNA_SOLVE,
            timeout=timeout,
        )

        self._model = ModelRestClient(self)
        self._solve_job = SolveJobRestClient(self)
        self._qpu_token = QpuTokenRestClient(self)
        self._info = InfoRestClient(self)

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

    @property
    def model(self) -> IModelRestClient:
        """
        Returns a model rest client.

        Returns
        -------
        IModelRestClient
        """
        return self._model

    @property
    def solve_job(self) -> ISolveJobRestClient:
        """
        Returns a solve job rest client.

        Returns
        -------
        ISolveJobRestClient
        """
        return self._solve_job

    @property
    def qpu_token(self) -> IQpuTokenRestClient:
        """
        Returns a qpu token rest client.

        Returns
        -------
        IQpuTokenRestClient
        """
        return self._qpu_token

    @property
    def info(self) -> IInfoRestClient:
        """
        Returns an info rest client.

        Returns
        -------
        IInfoRestClient
        """
        return self._info
