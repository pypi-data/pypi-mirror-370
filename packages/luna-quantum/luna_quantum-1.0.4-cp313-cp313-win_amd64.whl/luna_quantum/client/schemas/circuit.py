from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from luna_quantum.client.schemas.enums.circuit import (
    CircuitProviderEnum,
    CircuitStatusEnum,
)


class CircuitJob(BaseModel):
    """
    Object responsible of retrieving a circuit solution.

    Attributes
    ----------
    id: str
        Id of the circuit job.
    provider: CircuitProviderEnum
        The provider used to solve this circuit.
    params: Dict[str, Any]
        Additional parameters that were used to create the circuit.
    """

    id: str
    provider: CircuitProviderEnum
    params: dict[str, Any] | None = None


class CircuitResult(BaseModel):
    """
    The result of solving the circuit.

    Attributes
    ----------
    result: Optional[Dict[str, Any]]
        The result if the job succeeded. Otherwise None
    error: Optional[str]
        The error message if the job failed. Otherwise None
    status: CircuitStatusEnum
        The job status.
    """

    status: CircuitStatusEnum
    result: dict[str, Any] | None = None
    error_message: str | None = None
