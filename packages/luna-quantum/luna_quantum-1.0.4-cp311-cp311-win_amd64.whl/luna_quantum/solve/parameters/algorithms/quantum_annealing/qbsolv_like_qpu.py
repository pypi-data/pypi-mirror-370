from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params import (
    Decomposer,
    QuantumAnnealingParams,
)
from luna_quantum.solve.parameters.backends import DWaveQpu
from luna_quantum.solve.parameters.mixins.qbsolv_like_mixin import QBSolvLikeMixin


class QBSolvLikeQpu(QBSolvLikeMixin, LunaAlgorithm[DWaveQpu]):
    """
    QBSolv-like algorithm for QPU.

    QBSolv QPU splits the problem into parts and solves them using the Tabu Search
    algorithm. For this purpose, the DWaveSampler is used.

    Attributes
    ----------
    decomposer_size: int
        Size for the decomposer. Determines the maximum subproblem size to be sent to
        the quantum processor, with larger values potentially improving solution quality
        at the cost of increased processing time.
    rolling: bool
        Whether to use rolling for the solver. When enabled, this allows for smoother
        transitions between subproblems during the decomposition process.
    rolling_history: float
        Rolling history parameter for the solver. Controls how much previous iteration
        information is considered when solving subsequent subproblems.
    max_iter: int | None
        Maximum number of iterations. Limits the total number of decomposition and
        solving cycles performed by the algorithm.
    max_time: int
        Time in seconds after which the algorithm will stop. Provides a time-based
        stopping criterion regardless of convergence status.
    convergence: int
        Number of iterations with unchanged output to terminate algorithm. Higher values
        ensure more stable solutions but may increase computation time.
    target: float | None
        Energy level that the algorithm tries to reach. If this target energy is
        achieved, the algorithm will terminate early.
    rtol: float
        Relative tolerance for convergence. Used when comparing energy values between
        iterations to determine if convergence has been reached.
    atol: float
        Absolute tolerance for convergence. Used alongside rtol when comparing energy
        values to determine convergence.
    num_reads: int
        Number of reads for the solver.
    num_retries: int
        Number of retries for the solver.
    quantum_annealing_params: QuantumAnnealingParams
        Quantum annealing parameters.
    decomposer: Decomposer
        Decomposer: Breaks down problems into subproblems of manageable size
        Default is a Decomposer instance with default settings.
    """

    num_reads: int = 100
    num_retries: int = 0

    quantum_annealing_params: QuantumAnnealingParams = Field(
        default_factory=QuantumAnnealingParams
    )
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
        return "QLQ"

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
