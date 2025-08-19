from typing import Literal

from pydantic import BaseModel, Field, field_validator

from luna_quantum.solve.errors.solve_base_error import SolveBaseError


class MixerTypeError(SolveBaseError):
    """Custom Mixer type exception."""

    def __init__(self) -> None:
        super().__init__("XY-mixer type can only occur once.")


class XYMixer(BaseModel):
    """XY-mixer configuration.

    Attributes
    ----------
    types: list[Literal["even", "odd", "last"]]
        XY-ring-mixer pipeline
    """

    types: list[Literal["even", "odd", "last"]] = Field(
        default=["even", "odd", "last"],
        description="XY-ring-mixer types and order.",
    )

    @field_validator("types")
    @classmethod
    def _validate_type_once(
        cls, v: list[Literal["even", "odd", "last"]]
    ) -> list[Literal["even", "odd", "last"]]:
        if len(set(v)) < len(v):
            raise MixerTypeError
        return v


class AdvancedConfig(BaseModel):
    """Additional FlexQAOA algorithm configuration.

    Attributes
    ----------
    mixer: XYMixer | Dict
        Mixer types in XY-ring-mixer. Default: `["even", "odd", "last"]`
    parallel_indicators: bool
        Toggle to apply indicator functions in parallel. Does not affect sampling
        performance of QAOA, but only circuit metrics, like number of qubits and
        circuit depth.
    discard_slack: bool
        Discard slack qubits in evaluation, i.e. only measure on the binary variables of
        the initial problem. This requires an auxilary cost function that penalizes
        infeasible solutions.
    infeas_penalty: float | None
        Penalty for infeasible solutions if `discard_slack` is activated. By defalt,
        10 times the max absolute intial bias is chosen.
    """

    mixer: XYMixer = Field(
        default_factory=lambda: XYMixer(),
        description='Mixer types in XY-ring-mixer. Default: `["even", "odd", "last"]`',
    )
    parallel_indicators: bool = Field(
        default=True,
        description="Toggle to apply indicator functions in parallel. Does not affect "
        "sampling performance of QAOA, but only circuit metrics, "
        "like number of qubits and circuit depth.",
    )
    discard_slack: bool = Field(
        default=False,
        description="Discard slack qubits in evaluation, i.e. only measure on the "
        "binary variables of the initial problem. This requires an auxilary cost "
        "function that penalizes infeasible solutions.",
    )
    infeas_penalty: float | None = Field(
        default=None,
        ge=0,
        description="Penalty for infeasible solutions if `discard_slack` is activated."
        "By defalt, 10 times the max absolute intial bias is chosen.",
    )
