from __future__ import annotations

import numpy as np
from pydantic import BaseModel, Field, model_validator

from luna_quantum.solve.errors.solve_base_error import SolveBaseError


class QAOAParamsMismatchError(SolveBaseError):
    """QAOA Parameters mismatch in length."""

    def __init__(self, num_betas: int, num_gammas: int) -> None:
        super().__init__(f"Parameter length must match: {num_betas=} {num_gammas=}")


class BasicQAOAParams(BaseModel):
    """Individual QAOA Parameters.

    Parameters `betas` and `gammas` need to be of same size.

    Attributes
    ----------
    betas: list[float]
        List of beta parameters for the mixer layers in QAOA.
    gammas: list[float]
        List of gamma parameters for the cost layers in QAOA.
    """

    betas: list[float] = Field(
        description="List of beta parameters for the mixer layers in QAOA."
    )
    gammas: list[float] = Field(
        description="List of gamma parameters for the cost layers in QAOA."
    )

    @property
    def reps(self) -> int:
        """Returns the number of layers."""
        return len(self.betas)

    @model_validator(mode="after")
    def _check_matching(self) -> BasicQAOAParams:
        if len(self.betas) != len(self.gammas):
            raise QAOAParamsMismatchError(len(self.betas), len(self.gammas))
        return self


class LinearQAOAParams(BaseModel):
    """Linear QAOA Parameters.

    Linearly decreasing beta parameters from `delta_beta` to zero. Linearly growing
    paramters from zero to `delta_gamma`.

    Attributes
    ----------
    delta_beta: float
        Parameter scaling for the beta paramters for the mixer layers in QAOA.
    delta_gamma: float
        Parameters scaling for the gamma parameters for the cost layers in QAOA.
    """

    delta_beta: float = Field(
        description="Parameter scaling for the beta paramters for the mixer layers in "
        "QAOA."
    )
    delta_gamma: float = Field(
        description="Parameters scaling for the gamma parameters for the cost layers "
        "in QAOA."
    )


class RandomQAOAParams(BaseModel):
    """Uniform random QAOA Parameter within predefined value ranges.

    Attributes
    ----------
    seed: int | None
        Seed for random number generator.
    beta_range: tuple[float, float]
        Value range for uniform random beta parameters (mixer layer).
    gamma_range: tuple[float, float]
        Value range for uniform random gamma parameters (cost layer).
    """

    seed: int | None = Field(
        default=None, description="Seed for random number generator."
    )
    beta_range: tuple[float, float] = Field(
        default=(0, 2 * np.pi),
        description="Value range for uniform random beta parameters (mixer layer).",
    )
    gamma_range: tuple[float, float] = Field(
        default=(0, 2 * np.pi),
        description="Value range for uniform random gamma parameters (cost layer).",
    )
