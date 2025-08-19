from typing import Literal

from pydantic import BaseModel, Field

from luna_quantum.solve.parameters.algorithms.base_params.scipy_optimizer import (
    ScipyOptimizerParams,
)


class LinearOptimizerParams(ScipyOptimizerParams):
    """Optimizer for tuning a linear schedule of QAOA parameters.

    Optimizes onyl two parameters: `delta_beta` and `delta_gamma` with the default
    ScipyOptimizer.

    Wrapper for scipy.optimize.minimize. See
    [SciPy minimize documentation](
    https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html)
    for more information of the available methods and parameters.

    Attributes
    ----------
    method: ScipyOptimizerMethod
        Type of solver. See
        [SciPy minimize documentation](
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html)
        for supported methods.
    tol: float | None
        Tolerance for termination.
    bounds: None | tuple[float, float] | list[tuple[float, float]]
        Bounds on variables for Nelder-Mead, L-BFGS-B, TNC, SLSQP, Powell,
        trust-constr, COBYLA, and COBYQA methods. None is used to specify no bounds,
        `(min, max)` is used to specify bounds for all variables. A sequence of
        `(min, max)` can be used to specify bounds for each parameter individually.
    jac: None | Literal["2-point", "3-point", "cs"]
        Method for computing the gradient vector. Only for CG, BFGS, Newton-CG,
        L-BFGS-B, TNC, SLSQP, dogleg, trust-ncg, trust-krylov, trust-exact and
        trust-constr.
    hess: None | Literal["2-point", "3-point", "cs"]
        Method for computing the Hessian matrix. Only for Newton-CG, dogleg, trust-ncg,
        trust-krylov, trust-exact and trust-constr.
    maxiter: int
        Maximum number of iterations to perform. Depending on the method
        each iteration may use several function evaluations. Will be ignored for TNC
        optimizer. Default: 100
    options: dict[str, float]
        A dictionary of solver options.
    """

    optimizer_type: Literal["linear"] = "linear"


class CombinedOptimizerParams(BaseModel):
    """Combination of LinearOptimizer and ScipyOptimizer.

    Optimizer that first performs an optimization of the linear schedule and then
    fine tunes individual parameters.


    Attributes
    ----------
    linear: LinearOptimizerParams | Dict
        Parameters of the linear optimizer.
    fine_tune: ScipyOptimizerParams | Dict
        Parameters of the fine tuning optimizer.
    """

    optimizer_type: Literal["combined"] = "combined"
    linear: LinearOptimizerParams = Field(
        default_factory=lambda: LinearOptimizerParams()
    )
    fine_tune: ScipyOptimizerParams = Field(
        default_factory=lambda: ScipyOptimizerParams()
    )


class InterpolateOptimizerParams(BaseModel):
    """Optimizer with sequentially increasing number of QAOA layers.

    Optimizer that starts with `reps` iteration and interpolates sequentially in
    `reps_step` steps to `reps_end`. In between it performs a full optimization routine
    tunes individual parameters.

    Attributes
    ----------
    optimiezr: LinearOptimizerParams | ScipyOptimizerParams | Dict
        Parameters of the optimizer.
    reps_step: int
        Number of QAOA layers added for one interpolation.
    reps_end: int
        Final number of QAOA layers to be reached.
    """

    optimizer_type: Literal["interpolate"] = "interpolate"
    optimizer: ScipyOptimizerParams | LinearOptimizerParams = Field(
        default_factory=lambda: ScipyOptimizerParams()
    )
    reps_step: int = Field(default=1, ge=1)
    reps_end: int = Field(default=10, ge=1)
