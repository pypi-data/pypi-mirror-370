from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params import (
    Decomposer,
    QuantumAnnealingParams,
)
from luna_quantum.solve.parameters.backends import DWaveQpu
from luna_quantum.solve.parameters.constants import DEFAULT_ATOL, DEFAULT_RTOL


class ParallelTemperingQpu(
    LunaAlgorithm[DWaveQpu],
):
    """
    Parameters for the Parallel Tempering QPU solver.

    Parallel Tempering uses multiple model procedures per temperature.
    During the cooling process, an exchange of replicas can take place between the
    parallel procedures, thus enabling higher energy mountains to be overcome.

    Attributes
    ----------
    n_replicas: int
        Number of system replicas to simulate at different temperatures. More replicas
        provide better temperature coverage but increase computational cost.
        Default is 2, which is minimal but can still provide benefits over
        single-temperature methods.
    random_swaps_factor: int
        Factor controlling how frequently random swap attempts occur between replicas.
        Higher values increase mixing between replicas but add overhead.
        Default is 1, balancing mixing with efficiency.
    max_iter: int | None
        Maximum number of iterations. Controls how many rounds of replica exchange
        are performed. Higher values allow more thorough exploration.
        Default is 100.
    max_time: int
        Maximum time in seconds that the algorithm is allowed to run.
        Default is 5.
    convergence: int
        Number of consecutive iterations with no improvement required to consider
        the algorithm converged. Default is 3.
    target: float | None
        Target energy value. If reached, the algorithm will terminate.
        Default is None, meaning no target is set.
    rtol: float
        Relative tolerance for convergence checking. Default is DEFAULT_RTOL.
    atol: float
        Absolute tolerance for convergence checking. Default is DEFAULT_ATOL.
    num_reads: int
        Number of annealing cycles to perform on the D-Wave QPU. Default is 100.
    num_retries: int
        Number of attempts to retry embedding the problem onto the quantum hardware.
        Default is 0.
    fixed_temp_sampler_num_sweeps: int
        Number of Monte Carlo sweeps to perform, where one sweep attempts to update all
        variables once. More sweeps produce better equilibrated samples but increase
        computation time. Default is 10,000, which is suitable for thorough exploration
        of moderate-sized problems.
    fixed_temp_sampler_num_reads: int | None
        Number of independent sampling runs to perform. Each run produces one sample
        from the equilibrium distribution. Multiple reads provide better statistical
        coverage of the solution space. Default is None, which typically defaults to 1
        or matches the number of initial states provided.
    quantum_annealing_params: QuantumAnnealingParams
        Configuration for the quantum annealing process on D-Wave hardware.
        Contains settings for anneal schedule, flux biases, and other QPU-specific
        parameters. See QuantumAnnealingParams documentation for details.
    decomposer: Decomposer
        Decomposer: Breaks down problems into subproblems of manageable size
        Default is a Decomposer instance with default settings.
    """

    n_replicas: int = 2
    random_swaps_factor: int = 1
    max_iter: int | None = 100
    max_time: int = 5
    convergence: int = 3
    target: float | None = None
    rtol: float = DEFAULT_RTOL
    atol: float = DEFAULT_ATOL

    num_reads: int = 100
    num_retries: int = 0

    fixed_temp_sampler_num_sweeps: int = 10_000
    fixed_temp_sampler_num_reads: int | None = None

    quantum_annealing_params: QuantumAnnealingParams = Field(
        default_factory=QuantumAnnealingParams
    )

    decomposer: Decomposer = Field(default_factory=Decomposer)

    # does not support random_swaps_factor variable of parallel tempering parameters
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
        return "PTQ"

    @classmethod
    def get_default_backend(cls) -> DWaveQpu:
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
        return DWaveQpu()

    @classmethod
    def get_compatible_backends(cls) -> tuple[type[DWaveQpu], ...]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """
        return (DWaveQpu,)
