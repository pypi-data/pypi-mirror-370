from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params.tabu_search_params import (
    TabuSearchParams,
)
from luna_quantum.solve.parameters.backends import DWave


class TabuSearch(TabuSearchParams, LunaAlgorithm[DWave]):
    """
    Extended parameters for the Tabu Search optimization algorithm.

    Tabu Search is a metaheuristic that enhances local search by maintaining a
    "tabu list" of recently visited solutions to avoid cycling. It systematically
    explores the solution space by allowing non-improving moves when no improving moves
    exist, while preventing revisiting recent solutions.

    This class extends the basic TabuSearch with additional parameters for fine-tuning
    the search process, including restart strategies and early termination conditions.

    Attributes
    ----------
    initial_states: Any | None
        Starting states for the search. Allows the algorithm to begin from promising
        regions rather than random points. If fewer states than num_reads are provided,
        additional states are generated according to initial_states_generator.
        Default is None (random starting states).
    seed: int | None
        Random seed for reproducible results. With identical parameters and seed,
        results will be identical (unless timeout limits are reached, as finite
        clock resolution can affect execution). Default is None (random seed).
    num_restarts: int
        Maximum number of tabu search restarts per read. Restarts help escape deep
        local minima by starting fresh from new points after the initial search stalls.
        Setting to zero results in a simple tabu search without restarts.
        Default is 1,000,000, allowing many restarts if needed.
    energy_threshold: float | None
        Target energy value that triggers termination if found. Allows early stopping
        when a sufficiently good solution is discovered. Default is None (run until
        other stopping criteria are met).
    coefficient_z_first: int | None
        Controls the number of variable updates in the first simple tabu search (STS).
        The actual limit is max(variables*coefficient_z_first, lower_bound_z).
        Defaults to 10,000 for small problems (≤500 variables) and 25,000 for larger
        ones. Higher values allow more thorough exploration of the initial solution
        neighborhood.
    coefficient_z_restart: int | None
        Controls the number of variable updates in restarted tabu searches.
        Similar to coefficient_z_first but for restart phases. Default is
        coefficient_z_first/4, allowing faster exploration during restarts. This
        typically results in broader but less deep searches after restarts.
    lower_bound_z: int | None
        Minimum number of variable updates for all tabu searches. Ensures a thorough
        search even for small problems. Default is 500,000. Setting too low may
        result in premature termination before finding good solutions.
    num_reads: int | None
        Number of independent runs of the tabu algorithm, each producing one solution.
        Multiple reads increase the chance of finding the global optimum by starting
        from different initial states. If None, matches the number of initial states
        provided (or performs just one read if no initial states are given).
    tenure: int | None
        Length of the tabu list - the number of recently visited solutions that are
        forbidden. Larger values help escape deeper local minima but may slow
        exploration. Default is 1/4 of the number of variables up to a maximum of 20.
        A good tenure balances diversification (exploring new regions) with
        intensification (focusing on promising areas).
    timeout: float
        Maximum running time in milliseconds per read before the algorithm stops,
        regardless of convergence. Default is 100, which is suitable for small to
        medium-sized problems. For larger problems, consider increasing this value
        to allow sufficient exploration time.
    initial_states_generator: Literal["none", "tile", "random"]
        Controls how to handle situations where fewer initial states are provided
        than num_reads:

        - "none": Raises an error if insufficient initial states
        - "tile": Reuses provided states by cycling through them
        - "random": Generates additional random states as needed

        Default is "random", which maximizes search space coverage when the number
        of provided initial states is insufficient.
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
        return "TS"

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
