from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params import (
    SimulatedAnnealingParams,
)
from luna_quantum.solve.parameters.backends import DWave


class SimulatedAnnealing(SimulatedAnnealingParams, LunaAlgorithm[DWave]):
    """
    Simulated Annealing optimization algorithm.

    Simulated Annealing mimics the physical annealing process where a material is heated
    and then slowly cooled to remove defects. In optimization, this translates to
    initially accepting many non-improving moves (high temperature) and gradually
    becoming more selective (cooling) to converge to an optimum.

    This class inherits all parameters from SimulatedAnnealingParams, providing a
    complete set of controls for fine-grained customization of the annealing process.

    Attributes
    ----------
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
        with numpy.array. Default is None, which generates a schedule based on
        beta_range and
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
        number of initial states (or just one read if no initial states are
        provided).
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
        return "SA"

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
