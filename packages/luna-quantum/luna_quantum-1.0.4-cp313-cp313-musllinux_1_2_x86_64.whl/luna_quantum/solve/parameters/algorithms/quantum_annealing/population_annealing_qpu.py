from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params import (
    Decomposer,
    QuantumAnnealingParams,
)
from luna_quantum.solve.parameters.backends import DWaveQpu


class PopulationAnnealingQpu(LunaAlgorithm[DWaveQpu]):
    """
    Parameters for the Population Annealing QPU algorithm.

    Population Annealing uses a sequential Monte Carlo method to minimize the energy of
    a population. The population consists of walkers that can explore their
    neighborhood during the cooling process. Afterwards, walkers are removed and
    duplicated using bias to lower energy. Eventually, a population collapse occurs
    where all walkers are in the lowest energy state.

    Attributes
    ----------
    num_reads: int
        Number of annealing cycles to perform on the D-Wave QPU. Default is 100.
    num_retries: int
        Number of attempts to retry embedding the problem onto the quantum hardware.
        Default is 0.
    max_iter: int
        Maximum number of iterations. Controls how many rounds of annealing and
        population adjustments are performed. Default is 20.
    max_time: int
        Maximum time in seconds that the algorithm is allowed to run. Serves as
        a stopping criterion alongside max_iter. Default is 2.
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
    decomposer: Decomposer
        Decomposer: Breaks down problems into subproblems of manageable size
        Default is a Decomposer instance with default settings.
    quantum_annealing_params: QuantumAnnealingParams
        Parameters that control the quantum annealing process, including annealing
        schedule, temperature settings, and other quantum-specific parameters. These
        settings determine how the system transitions from quantum superposition to
        classical states during the optimization process.
    """

    num_reads: int = 100
    num_retries: int = 0
    max_iter: int = 20
    max_time: int = 2
    fixed_temp_sampler_num_sweeps: int = 10_000
    fixed_temp_sampler_num_reads: int | None = None
    decomposer: Decomposer = Field(default_factory=Decomposer)

    quantum_annealing_params: QuantumAnnealingParams = Field(
        default_factory=QuantumAnnealingParams
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
        return "PAQ"

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
