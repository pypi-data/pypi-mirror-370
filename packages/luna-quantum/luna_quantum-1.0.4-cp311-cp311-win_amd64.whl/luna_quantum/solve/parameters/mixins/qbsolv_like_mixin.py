from pydantic import BaseModel

from luna_quantum.solve.parameters.constants import DEFAULT_ATOL, DEFAULT_RTOL


class QBSolvLikeMixin(BaseModel):
    """
    QBSolvLikeMixin.

    Attributes
    ----------
    decomposer_size: int
        Size for the decomposer, which determines the maximum subproblem size to be
        handled in each iteration. Larger values may produce better solutions but
        increase computational complexity exponentially. Default is 50, which balances
        solution quality with reasonable runtime.
    rolling: bool
        Whether to use rolling window decomposition for the solver. When enabled,
        this allows for overlapping subproblems with shared variables, which can
        improve solution quality by better handling interactions across subproblem
        boundaries. Default is True.
    rolling_history: float
        Rolling history factor controlling how much of previous subproblem solutions
        are considered when solving subsequent subproblems. Higher values incorporate
        more historical information but may slow convergence to new solutions.
        Default is 0.15 (15% retention).
    max_iter: int | None
        Maximum number of iterations (decomposition and solving cycles) to perform.
        Higher values allow for more thorough optimization but increase runtime.
        Default is 100.
    max_time: int
        Time in seconds after which the algorithm will stop, regardless of convergence
        status. Provides a hard time limit for time-constrained applications.
        Default is 5.
    convergence: int
        Number of iterations with unchanged output to terminate algorithm. Higher values
        ensure more stable solutions but may increase computation time unnecessarily
        if the algorithm has already found the best solution. Default is 3.
    target: float | None
        Energy level that the algorithm tries to reach. If this target energy is
        achieved, the algorithm will terminate early. Default is None, meaning the
        algorithm will run until other stopping criteria are met.
    rtol: float
        Relative tolerance for convergence. Used when comparing energy values between
        iterations to determine if significant improvement has occurred. Default uses
        DEFAULT_RTOL.
    atol: float
        Absolute tolerance for convergence. Used alongside rtol when comparing energy
        values to determine if the algorithm has converged. Default uses DEFAULT_ATOL.
    """

    decomposer_size: int = 50
    rolling: bool = True
    rolling_history: float = 0.15
    max_iter: int | None = 100
    max_time: int = 5
    convergence: int = 3
    target: float | None = None
    rtol: float = DEFAULT_RTOL
    atol: float = DEFAULT_ATOL
