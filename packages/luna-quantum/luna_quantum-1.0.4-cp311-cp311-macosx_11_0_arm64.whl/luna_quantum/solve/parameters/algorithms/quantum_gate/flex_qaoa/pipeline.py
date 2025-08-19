from pydantic import BaseModel, Field


class OneHotParams(BaseModel):
    """Implements one-hot constraints through XY-mixers."""


class IndicatorFunctionParams(BaseModel):
    """Implements inequality constraints via indicator functions.

    Attributes
    ----------
    penalty: float | None
        Custom penalty factor for indicator functions. If none set, automatically
        determined through upper and lower bounds.
    penalty_scaling: float
        Scaling of automatically determined penalty factor. Default: 2
    """

    penalty: float | None = Field(
        default=None,
        ge=0,
        description="Custom penalty factor for indicator functions. If none set, "
        "automatically determined through upper and lower bounds.",
    )
    penalty_scaling: float = Field(
        default=2,
        ge=0,
        description="Scaling of automatically determined penalty factor. Default: 2",
    )


class QuadraticPenaltyParams(BaseModel):
    """Implements all constraints through quadratic penalties.

    Adds penalty terms to the objective. Adds slack variables for inequality constraints
    if neccessaray.

    Attributes
    ----------
    penalty: float | None
        Custom penalty factor for quadratic penalty terms. If none is set, it is
        automatically determined by taking 10 times the maximum absolute initial bias.
    """

    penalty: float | None = Field(
        default=None,
        ge=0,
        description="Custom penalty factor for quadratic penalty terms. If none set, "
        "automatically determined by taking 10 times the maximum absolute initial "
        "bias.",
    )


class PipelineParams(BaseModel):
    """Defines the modular Constrained QAOA Pipeline.

    By default all features are enabled.

    Attributes
    ----------
    indicator_function: IndicatorFunctionParams | Dict | None
        Whether to implement inequality constraints with indicator functions. Disable
        with setting to `None`.
    one_hot: OneHotParams | Dict | None
        Whether to implement inequality constraints with indicator functions. Disable
        with setting to `None`.
    quadratic_penalty: QuadraticPenaltyParams | Dict | None
        Whether to implement inequality constraints with indicator functions. Disable
        with setting to `None`.
    """

    indicator_function: IndicatorFunctionParams | None = Field(
        default_factory=lambda: IndicatorFunctionParams(),
        description="Whether to implement inequality constraints with indicator "
        "functions. Disable with setting to `None`.",
    )
    one_hot: OneHotParams | None = Field(
        default_factory=lambda: OneHotParams(),
        description="Whether to implement inequality constraints with indicator "
        "functions. Disable with setting to `None`.",
    )
    quadratic_penalty: QuadraticPenaltyParams | None = Field(
        default_factory=lambda: QuadraticPenaltyParams(),
        description="Whether to implement inequality constraints with indicator "
        "functions. Disable with setting to `None`.",
    )
