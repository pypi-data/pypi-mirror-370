from __future__ import annotations

from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params import (
    SimulatedAnnealingBaseParams,
)
from luna_quantum.solve.parameters.backends import DWave
from luna_quantum.solve.parameters.mixins.qbsolv_like_mixin import QBSolvLikeMixin


class QBSolvLikeSimulatedAnnealing(LunaAlgorithm[DWave], QBSolvLikeMixin):
    """
    QBSolv Like Simulated Annealing solver.

    QBSolv Like Simulated Annealing breaks down the problem and solves the parts
    individually using a classic solver that uses Simulated Annealing.
    This particular implementation uses hybrid.SimulatedAnnealingSubproblemSampler
    (https://docs.ocean.dwavesys.com/projects/hybrid/en/stable/reference/samplers.html#simulatedannealingsubproblemsampler)
    as a sampler for the subproblems to achieve a QBSolv like behaviour.

    This class combines parameters from multiple sources:
    - QBSolvLikeMixin: Provides parameters for the QBSolv-like decomposition approach
    - SimulatedAnnealingParams: Provides parameters specific to simulated annealing

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
    num_reads : Union[int, None]
        Number of independent runs of the algorithm, each producing one solution sample.
        Multiple reads with different random starting points increase the chance of
        finding the global optimum. Default is None, which matches the number of initial
        states (or just one read if no initial states are provided).
    num_sweeps : Union[int, None]
        Number of iterations/sweeps per run, where each sweep updates all variables
        once. More sweeps allow more thorough exploration but increase runtime.
        Default is 1,000, suitable for small to medium problems.
    beta_range : Union[List[float], Tuple[float, float], None]
        The inverse temperature (β=1/T) schedule endpoints, specified as [start, end].
        A wider range allows more exploration. Default is calculated based on the
        problem's energy scale to ensure appropriate acceptance probabilities.
    beta_schedule_type : Literal["linear", "geometric"]
        How beta values change between endpoints:
        - "linear": Equal steps (β₁, β₂, ...) - smoother transitions
        - "geometric": Multiplicative steps (β₁, r·β₁, r²·β₁, ...) - spends more time at
          lower temperatures for fine-tuning
        Default is "geometric", which often performs better for optimization problems.
    initial_states_generator : Literal["none", "tile", "random"]
        How to handle cases with fewer initial states than num_reads:
        - "none": Raises error if insufficient initial states
        - "tile": Reuses provided states by cycling through them
        - "random": Generates additional random states as needed
        Default is "random", which maximizes exploration.
    """

    simulated_annealing: SimulatedAnnealingBaseParams = Field(
        default_factory=SimulatedAnnealingBaseParams
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
        return "QLSA"

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
    def get_compatible_backends(cls) -> tuple[type[DWave]]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return (DWave,)
