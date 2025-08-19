from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from luna_quantum.client.schemas.qpu_token.token_provider import (
    RestAPITokenProvider,
)


class SolveJobCreate(BaseModel):
    """
    Schema for creating a new solve job.

    Attributes
    ----------
    model_id : str
        Unique identifier of the model to be solved.

    solver_name : str
        Name of the solver algorithm to be used for the computation.

    provider : str
        Name of the provider that will execute the job.

    parameters : dict[str, Any]
        Dictionary of solver-specific parameters options.

    qpu_tokens : RestAPITokenProvider | None, optional
        Authentication tokens for accessing QPU providers.
        Contains provider-specific authentication credentials.

    name : str | None, optional
        Optional user-defined name for the solve job.
    """

    model_id: str  # id of the model
    solver_name: str
    provider: str
    parameters: dict[str, Any]
    qpu_tokens: RestAPITokenProvider | None = None
    name: str | None = None
