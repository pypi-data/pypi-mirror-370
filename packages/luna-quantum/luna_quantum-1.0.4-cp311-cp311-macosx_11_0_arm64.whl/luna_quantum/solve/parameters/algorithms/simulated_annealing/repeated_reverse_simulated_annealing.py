from __future__ import annotations

from typing import Any

from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params import (
    SimulatedAnnealingParams,
)
from luna_quantum.solve.parameters.backends import DWave


class RepeatedReverseSimulatedAnnealing(SimulatedAnnealingParams, LunaAlgorithm[DWave]):
    """
    Parameters for the Repeated Reverse Simulated Annealing solver.

    This algorithm applies principles similar to quantum reverse annealing but in a
    classical context. It starts from specified states, partially "reverses" the
    annealing by increasing temperature to explore nearby states, then re-anneals to
    find improved solutions. This process repeats for multiple iterations, refining
    solutions progressively.

    The approach is particularly effective for problems with complex energy landscapes
    where standard simulated annealing might get trapped in local optima.

    Attributes
    ----------
    num_reads_per_iter: list[int] | None
        Number of reads (independent runs) to perform in each iteration.
        Uses num_reads_per_iter[i] in iteration i, and num_reads_per_iter[-1] once
        the list is exhausted. If None, uses the num_reads value inherited from
        SimulatedAnnealingParams. This allows dynamic control of sampling intensity
        across iterations, typically starting with broader exploration and focusing
        on refinement in later iterations. Minimum list length: 1.
        Default is None.
    initial_states: Any | None
        Starting states for the first iteration. Each state defines values for all
        problem variables and serves as a starting point for the reverse annealing
        process. If fewer states than reads are provided, additional states are
        generated according to the initial_states_generator setting inherited from
        SimulatedAnnealingParams. Providing good initial states (e.g., from classical
        heuristics) can significantly improve solution quality.
        Default is None, which generates random initial states.
    timeout: float
        Maximum runtime in seconds before termination, regardless of other stopping
        criteria. Provides a hard time limit for time-constrained applications.
        Default is 5.0 seconds, which is suitable for small to medium-sized problems.
        For larger or more complex problems, consider increasing this value.
    max_iter: int
        Maximum number of reverse annealing iterations to perform. Each iteration
        involves: starting from the best states found so far, raising temperature to
        explore nearby configurations, then gradually cooling to refine solutions.
        More iterations generally improve solution quality but increase runtime.
        Default is 10, providing a good balance for most problems.
    target: Any | None
        Target energy value that triggers early termination if reached. Allows the
        algorithm to stop when a solution of sufficient quality is found, even before
        reaching max_iter or timeout. Default is None, which means the algorithm will
        run until other stopping criteria are met.

    num_sweeps_per_beta: int
        Number of sweeps to perform at each temperature before cooling. More sweeps
        per temperature allow better exploration at each temperature level.
        Default is 1, which works well for many problems.
    seed: Optional[int]
        Random seed for reproducible results. Using the same seed with identical
        parameters produces identical results. Default is None (random seed).
    beta_schedule: Sequence[float] | None
        Explicit sequence of beta (inverse temperature) values to use. Provides
        complete control over the cooling schedule. Format must be compatible
        with numpy.array.
        Default is None, which generates a schedule based on beta_range and
        beta_schedule_type.
    initial_states: Optional[Any]
        One or more starting states, each defining values for all problem variables.
        This allows the algorithm to start from promising regions rather than random
        points.
        Default is None (random starting states).
    randomize_order: bool
        When True, variables are updated in random order during each sweep.
        When False, variables are updated sequentially. Random updates preserve
        symmetry of the model but are slightly slower. Default is False for
        efficiency.
    proposal_acceptance_criteria: Literal["Gibbs", "Metropolis"]
        Method for accepting or rejecting proposed moves:
        - "Gibbs": Samples directly from conditional probability distribution
        - "Metropolis": Uses Metropolis-Hastings rule (accept if improving,
            otherwise accept with probability based on energy difference and
            temperature)
        Default is "Metropolis", which is typically faster and works well for most
        problems.
    num_reads : Union[int, None]
        Number of independent runs of the algorithm, each producing one solution
        sample. Multiple reads with different random starting points increase the
        chance of finding the global optimum. Default is None, which matches the
        number of initial
        states (or just one read if no initial states are provided).
    num_sweeps : Union[int, None]
        Number of iterations/sweeps per run, where each sweep updates all variables
        once. More sweeps allow more thorough exploration but increase runtime.
        Default is 1,000, suitable for small to medium problems.
    beta_range : Union[List[float], Tuple[float, float], None]
        The inverse temperature (β=1/T) schedule endpoints, specified as [start,
        end]. A wider range allows more exploration. Default is calculated based
        on the
        problem's energy scale to ensure appropriate acceptance probabilities.
    beta_schedule_type : Literal["linear", "geometric"]
        How beta values change between endpoints:
        - "linear": Equal steps (β₁, β₂, ...) - smoother transitions
        - "geometric": Multiplicative steps (β₁, r·β₁, r²·β₁, ...) - spends more
            time at lower temperatures for fine-tuning
        Default is "geometric", which often performs better for optimization
        problems.
    initial_states_generator : Literal["none", "tile", "random"]
        How to handle cases with fewer initial states than num_reads:
        - "none": Raises error if insufficient initial states
        - "tile": Reuses provided states by cycling through them
        - "random": Generates additional random states as needed
        Default is "random", which maximizes exploration.
    """

    num_reads_per_iter: list[int] | None = Field(default=None, min_length=1)
    initial_states: Any | None = None
    timeout: float = 5.0
    max_iter: int = 10
    target: Any | None = None

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
        return "RRSA"

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
