from __future__ import annotations

from typing import TYPE_CHECKING, Any

from luna_quantum.client.interfaces.clients.circuit_rest_client_i import (
    ICircuitRestClient,
)
from luna_quantum.client.schemas.circuit import CircuitJob, CircuitResult
from luna_quantum.client.schemas.create.circuit import CircuitIn
from luna_quantum.client.schemas.qpu_token.qpu_token import TokenProvider
from luna_quantum.client.schemas.qpu_token.token_provider import RestAPITokenProvider
from luna_quantum.client.utils.qpu_token_utils import QpuTokenUtils

if TYPE_CHECKING:
    from luna_quantum.client.schemas.enums.circuit import CircuitProviderEnum


class CircuitRestClient(ICircuitRestClient):
    """Implementation for circuit rest client."""

    _endpoint = "/circuits"

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
        if params is None:
            params = {}
        if qpu_tokens is not None:
            rest_qpu_tokens = RestAPITokenProvider.from_sdk_token_provider(
                TokenProvider.model_validate(qpu_tokens)
            )
        else:
            rest_qpu_tokens = None

        # try to retrieve qpu tokens from env variables
        if rest_qpu_tokens is None:
            qpu_tokens = QpuTokenUtils.patch_qpu_tokens_from_env()
            if qpu_tokens is not None:
                rest_qpu_tokens = RestAPITokenProvider.from_sdk_token_provider(
                    qpu_tokens
                )

        circuit_in: CircuitIn = CircuitIn(
            provider=provider,
            circuit=circuit,
            params=params,
            qpu_tokens=rest_qpu_tokens,
        )

        response = self._client.post(
            self._endpoint, content=circuit_in.model_dump_json(), **kwargs
        )

        response.raise_for_status()
        return CircuitJob(id=response.json(), provider=provider, params=params)

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
        url = f"{self._endpoint}/{job.id}/{job.provider.value}"
        if job.params is None:
            job.params = {}
        response = self._client.get(url, params=job.params, **kwargs)

        response.raise_for_status()
        return CircuitResult.model_validate(response.json())
