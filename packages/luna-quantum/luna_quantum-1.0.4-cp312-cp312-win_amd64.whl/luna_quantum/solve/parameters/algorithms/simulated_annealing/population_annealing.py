from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.backends import DWave


class PopulationAnnealing(LunaAlgorithm[DWave]):
    """
    Parameters for the Population Annealing algorithm.

    Population Annealing uses a sequential Monte Carlo method to minimize the energy of
    a population. The population consists of walkers that can explore their neighborhood
    during the cooling process. Afterwards, walkers are removed and duplicated using
    bias to lower energy. Eventually, a population collapse occurs where all walkers are
    in the lowest energy state.

    Attributes
    ----------
    max_iter: int
        Maximum number of annealing iterations (temperature steps) to perform. Each
        iteration involves lowering the temperature, allowing walkers to explore
        locally, and then resampling the population based on Boltzmann weights.
        Higher values allow for a more gradual cooling schedule, potentially finding
        better solutions but increasing computation time. Default is 20,
        which provides a reasonable balance for most problems.
    max_time: int
        Maximum time in seconds that the algorithm is allowed to run. Provides a hard
        time limit regardless of convergence or iteration status. Useful for
        time-constrained scenarios where some solution is needed within a specific
        timeframe. Default is 2, which is relatively aggressive and may need to be
        increased for complex problems.
    fixed_temp_sampler_num_sweeps: int
        Number of Monte Carlo sweeps to perform at each temperature level, where one
        sweep attempts to update all variables once. More sweeps allow walkers to
        explore their local configuration space more thoroughly, producing better
        equilibrated samples but increasing computation time. This parameter directly
        affects how well each walker samples its local energy landscape before
        resampling occurs. Default is 10,000, which is suitable for thorough exploration
        of moderate-sized problems.
    fixed_temp_sampler_num_reads: int | None
        Number of independent sampling runs to perform at each temperature level.
        Each run effectively initializes a separate walker in the population. Multiple
        reads provide better coverage of the solution space, increasing the diversity
        of the initial population and improving the chances of finding the global
        optimum. Default is None, which typically defaults to 1 or matches the number
    """

    max_iter: int = 20
    max_time: int = 2

    fixed_temp_sampler_num_sweeps: int = 10_000
    fixed_temp_sampler_num_reads: int | None = None

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
        return "PA"

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
