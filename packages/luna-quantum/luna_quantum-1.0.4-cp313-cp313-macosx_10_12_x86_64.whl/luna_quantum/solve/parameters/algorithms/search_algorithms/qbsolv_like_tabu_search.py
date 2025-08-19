from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params.tabu_search_params import (
    TabuSearchBaseParams,
)
from luna_quantum.solve.parameters.backends import DWave
from luna_quantum.solve.parameters.mixins.qbsolv_like_mixin import QBSolvLikeMixin


class QBSolvLikeTabuSearch(QBSolvLikeMixin, LunaAlgorithm[DWave]):
    """QbSolvLikeTabuSearch Parameters.

    QBSolv Like Tabu Search breaks down the problem and solves the parts individually
    using a classic solver that uses Tabu Search. This particular implementation uses
    hybrid.TabuSubproblemSampler (https://docs.ocean.dwavesys.com/projects/hybrid/en/stable/reference/samplers.html#tabusubproblemsampler)
    as a sampler for the subproblems to achieve a QBSolv like behaviour.

    This class combines parameters from two sources:
    - QBSolvLikeMixin: Provides parameters for the QBSolv-like decomposition approach
    - tabu_search_params: Nested parameter object for Tabu Search configuration

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
    tabu_search_params: TabuSearchBaseParams
        Nested configuration for Tabu Search algorithm parameters. Controls the
        behavior of the Tabu Search used to solve each subproblem, including
        parameters like tabu tenure, number of restarts, and timeout conditions.
        See TabuSearchParams class for details of contained parameters.
    """

    tabu_search_params: TabuSearchBaseParams = Field(
        default_factory=TabuSearchBaseParams
    )

    @property
    def algorithm_name(self) -> str:
        """
        Returns the name of the algorithm.

        This abstract property method is intended to be overridden by subclasses.
        It should provide the name of the algorithm being implemented.

        Returns
        -------
        str
            The name of the algorithm.
        """
        return "QLTS"

    @classmethod
    def get_default_backend(cls) -> DWave:
        """
        Return the default backend implementation.

        This property must be implemented by subclasses to provide
        the default backend instance to use when no specific backend
        is specified.

        Returns
        -------
            IBackend
                An instance of a class implementing the IBackend interface that serves
                as the default backend.
        """
        return DWave()

    @classmethod
    def get_compatible_backends(cls) -> tuple[type[DWave], ...]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return (DWave,)
