from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.backends import DWave
from luna_quantum.solve.parameters.constants import DEFAULT_ATOL, DEFAULT_RTOL


class ParallelTempering(LunaAlgorithm[DWave]):
    """
    Parameters for the Parallel Tempering (replica exchange) optimization algorithm.

    Parallel Tempering runs multiple copies ("replicas") of the system simultaneously
    at different temperatures. Periodically, replicas at adjacent temperatures can swap
    configurations, allowing high-temperature replicas to explore widely while
    low-temperature replicas exploit promising regions.

    This approach is particularly effective for problems with many local minima, as it
    combines the exploration benefits of high temperature with the exploitation benefits
    of low temperature.

    Attributes
    ----------
    n_replicas: int
        Number of system replicas to simulate at different temperatures. More replicas
        provide better temperature coverage but increase computational cost.
        Higher values allow for finer gradations between temperature levels, potentially
        improving the exchange of configurations between adjacent replicas.
        Default is 2, which is minimal but can still provide benefits over
        single-temperature methods.
    random_swaps_factor: int
        Factor controlling how frequently random swap attempts occur between replicas.
        Higher values increase mixing between replicas but add computational overhead.
        More frequent swaps help configurations move more quickly between temperature
        levels, allowing good solutions found at high temperatures to be refined at
        lower temperatures. Default is 1, balancing mixing with efficiency.
    max_iter: int | None
        Maximum number of iterations (temperature cycles) to perform. Each iteration
        involves sampling at all temperature levels and attempting exchanges between
        replicas. Higher values allow more thorough exploration but increase runtime.
        Default is 100.
    max_time: int
        Maximum time in seconds for the algorithm to run. Provides a hard time limit
        regardless of convergence or iteration status. Useful for time-constrained
        scenarios where some solution is needed within a specific timeframe.
        Default is 5.
    convergence: int
        Number of consecutive iterations without improvement before declaring
        convergence. Higher values ensure more stable solutions but may increase
        computation time unnecessarily if the algorithm has already found the best
        solution. Default is 3.
    target: float | None
        Target objective value that triggers termination if reached. Allows early
        stopping when a sufficiently good solution is found. Default is None, which
        means the algorithm will run until other stopping criteria are met.
    rtol: float
        Relative tolerance for convergence detection. Used when comparing objective
        values between iterations to determine if significant improvement has occurred.
        Default is DEFAULT_RTOL.
    atol: float
        Absolute tolerance for convergence detection. Used alongside rtol when comparing
        objective values to determine if the algorithm has converged. Default is
        DEFAULT_ATOL.
    fixed_temp_sampler_num_sweeps: int
        Number of Monte Carlo sweeps to perform at each temperature level, where one
        sweep attempts to update all variables once. More sweeps produce better
        equilibrated samples but increase computation time. This parameter controls
        how thoroughly each replica explores its local solution space before exchange
        attempts. Default is 10,000, which is suitable for thorough exploration of
        moderate-sized problems.
    fixed_temp_sampler_num_reads: int | None
        Number of independent sampling runs to perform at each temperature level.
        Each run produces one sample from the equilibrium distribution. Multiple reads
        provide better statistical coverage of the solution space at each temperature.
        Default is None, which typically defaults to 1 or matches the number of initial
        states provided.
    """

    n_replicas: int = 2
    random_swaps_factor: int = 1
    max_iter: int | None = 100
    max_time: int = 5
    convergence: int = 3
    target: float | None = None
    rtol: float = DEFAULT_RTOL
    atol: float = DEFAULT_ATOL

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
        return "PT"

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
