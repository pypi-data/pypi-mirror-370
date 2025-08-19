from typing import Literal

from pydantic import BaseModel, Field, field_validator

ScipyOptimizerMethod = Literal[
    "nelder-mead",
    "powell",
    "cg",
    "bfgs",
    "newton-cg",
    "l-bfgs-b",
    "tnc",
    "cobyla",
    "cobyqa",
    "slsqp",
    "trust-constr",
    "dogleg",
    "trust-ncg",
    "trust-exact",
    "trust-krylov",
    "NELDER-MEAD",
    "POWELL",
    "CG",
    "BFGS",
    "NEWTON-CG",
    "L-BFGS-B",
    "TNC",
    "COBYLA",
    "COBYQA",
    "SLSQP",
    "TRUST-CONSTR",
    "DOGLEG",
    "TRUST-NCG",
    "TRUST-EXACT",
    "TRUST-KRYLOV",
    "Nelder-Mead",
    "Newton-CG",
]


class ScipyOptimizerParams(BaseModel):
    """Wrapper for scipy.optimize.minimize.

    See [SciPy minimize documentation](
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
    bounds: None | list[tuple[float, float]]
        Bounds on variables for Nelder-Mead, L-BFGS-B, TNC, SLSQP, Powell,
        trust-constr, COBYLA, and COBYQA methods. `None` is used to specify no bounds.
        A sequence of `(min, max)` can be used to specify bounds for each parameter
        individually.
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

    method: ScipyOptimizerMethod = Field(
        default="cobyla",
        description="Type of solver. See "
        "https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.minimize.html"
        "for supported methods.",
    )
    tol: float | None = Field(
        default=None, ge=0, description="Tolerance for termination."
    )
    bounds: None | list[tuple[float, float]] = Field(
        default=None,
        description="Bounds on variables for Nelder-Mead, L-BFGS-B, TNC, SLSQP, Powell,"
        "trust-constr, COBYLA, and COBYQA methods. None is used to specify no bounds. "
        "A sequence of `(min, max)` can be used to specify bounds for each parameter "
        "individually.",
    )
    jac: None | Literal["2-point", "3-point", "cs"] = Field(
        default=None,
        description="Method for computing the gradient vector. Only for CG, BFGS, "
        "Newton-CG, L-BFGS-B, TNC, SLSQP, dogleg, trust-ncg, trust-krylov, trust-exact "
        "and trust-constr.",
    )
    hess: None | Literal["2-point", "3-point", "cs"] = Field(
        default=None,
        description="Method for computing the Hessian matrix. Only for Newton-CG, "
        "dogleg, trust-ncg, trust-krylov, trust-exact and trust-constr.",
    )
    maxiter: int = Field(
        default=100,
        ge=1,
        le=10000,
        description="Maximum number of iterations to perform. Depending on the method "
        "each iteration may use several function evaluations. Will be ignored for TNC "
        "optimizer.",
    )
    options: dict[str, float] = Field(
        default_factory=dict, description="A dictionary of solver options."
    )

    @field_validator("options", mode="after")
    @classmethod
    def _ensure_no_maxiter(cls, v: dict[str, float]) -> dict[str, float]:
        if "maxiter" in v:
            msg = "Please do not specify `maxiter` in options dict."
            raise ValueError(msg)
        return v
