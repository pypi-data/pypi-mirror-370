from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params import (
    Decomposer,
    QuantumAnnealingParams,
    SimulatedAnnealingBaseParams,
    TabuKerberosParams,
)
from luna_quantum.solve.parameters.backends import DWaveQpu
from luna_quantum.solve.parameters.constants import (
    DEFAULT_ATOL,
    DEFAULT_RTOL,
)


class Kerberos(
    LunaAlgorithm[DWaveQpu],
):
    """
    Kerberos hybrid quantum-classical optimization solver.

    Kerberos is a sophisticated hybrid solver that decomposes an optimization problem
    into subproblems and solves them using multiple techniques in parallel: Tabu Search,
    Simulated Annealing, and QPU (Quantum Processing Unit) sampling. It then combines
    the results and iteratively refines the solution.

    This approach leverages both classical and quantum resources efficiently, making it
    effective for large and complex optimization problems beyond the capacity of pure
    quantum approaches.

    Attributes
    ----------
    num_reads: int
        Number of output solutions to generate. Higher values provide better statistical
        coverage of the solution space but increase computational resources required.
        This parameter determines how many distinct solutions the algorithm will return
        after completion. Default is 100.
    num_retries: int
        Number of attempts to retry embedding the problem onto the quantum hardware
        if initial attempts fail. Useful for complex problems that may be challenging
        to map to the quantum processor's topology. Each retry attempts a different
        embedding strategy. Default is 0 (no retries).
    max_iter: int | None
        Maximum number of iterations for the solver. Each iteration involves running
        the three solvers (Tabu, SA, QPU) in parallel, combining their results, and
        refining the solution for the next iteration. Higher values allow more thorough
        exploration and refinement but increase runtime. Default is 100.
    max_time: int
        Maximum time in seconds for the solver to run. Provides a hard time limit
        regardless of convergence or iteration status. Once this time is reached,
        the solver returns the best solution found so far. Default is 5, which may
        need to be increased for large problems.
    convergence: int
        Number of consecutive iterations without improvement before declaring
        convergence. Higher values ensure more stable solutions by requiring consistent
        results across multiple iterations. Default is 3, which balances thoroughness
        with efficiency.
    target: float | None
        Target objective value that triggers termination if reached. Allows early
        stopping when a solution of sufficient quality is found. Default is None,
        which means the algorithm will run until other stopping criteria are met.
    rtol: float
        Relative tolerance for convergence detection. Used when comparing objective
        values between iterations to determine if significant improvement has occurred.
        Smaller values require more substantial improvements to continue. Default is
        DEFAULT_RTOL.
    atol: float
        Absolute tolerance for convergence detection. Used alongside rtol when
        comparing objective values to determine if the algorithm has converged.
        Smaller values enforce stricter convergence criteria. Default is DEFAULT_ATOL.
    quantum_annealing_params: QuantumAnnealingParams
        Nested configuration for quantum annealing parameters used by the QPU component
        of the hybrid solver. Controls aspects like annealing schedule, chain strength,
        and programming thermalization time. These parameters can significantly impact
        the quality of solutions found by the quantum component. Default is a
        QuantumAnnealingParams instance with default settings.
    tabu_kerberos_params: TabuKerberosParams
        Nested configuration for tabu search parameters used by the Tabu component of
        the hybrid solver. Controls aspects like tabu tenure, number of iterations,
        and neighborhood exploration strategy. The Tabu component helps the algorithm
        systematically explore promising regions while avoiding cycles. Default is a
        TabuKerberosParams instance with default settings.
    decomposer: Decomposer
        Decomposer: Breaks down problems into subproblems of manageable size
        Default is a Decomposer instance with default settings.
    """

    num_reads: int = 100
    num_retries: int = 0
    max_iter: int | None = 100
    max_time: int = 5
    convergence: int = 3
    target: float | None = None
    rtol: float = DEFAULT_RTOL
    atol: float = DEFAULT_ATOL
    simulated_annealing_params: SimulatedAnnealingBaseParams = Field(
        default_factory=SimulatedAnnealingBaseParams
    )
    quantum_annealing_params: QuantumAnnealingParams = Field(
        default_factory=QuantumAnnealingParams
    )
    tabu_kerberos_params: TabuKerberosParams = Field(default_factory=TabuKerberosParams)
    decomposer: Decomposer = Field(default_factory=Decomposer)

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
        return "K"

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
