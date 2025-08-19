from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.algorithms.base_params import (
    QuantumAnnealingParams,
)
from luna_quantum.solve.parameters.backends import DWaveQpu


class QuantumAnnealing(QuantumAnnealingParams, LunaAlgorithm[DWaveQpu]):
    """
    Quantum Annealing algorithm for physical quantum processors (QPUs).

    Quantum Annealing is a metaheuristic that leverages quantum effects to find the
    ground state of a system, corresponding to the optimal solution of an optimization
    problem.

    The process starts in a quantum superposition of all possible states, and gradually
    evolves the system according to a time-dependent Hamiltonian, exploiting quantum
    tunneling to potentially escape local minima more effectively than classical
    methods.

    This implementation is specifically for D-Wave quantum annealers or similar
    hardware.

    This class inherits all parameters from QuantumAnnealingParams, providing
    a complete set of controls for the quantum annealing process on hardware devices.

    Attributes
    ----------
    anneal_offsets: list[float] | None
        Per-qubit time offsets for the annealing path in normalized annealing time
        units. List of floats with length equal to the number of qubits. Default is
        None.
    anneal_schedule: list[tuple[float, float]] | None
        Custom schedule for the annealing process as a list of (time, s) pairs.
        Time is in normalized units [0, 1] and s is the annealing parameter [0, 1].
        Default is None.
    annealing_time: float | None
        Duration of the annealing process in microseconds. Must be within the range
        supported by the QPU hardware. Default is None.
    auto_scale: bool | None
        Whether to automatically normalize the problem energy range to use the full
        range of h and J values supported by the hardware. Default is None.
    fast_anneal: bool
        Use accelerated annealing protocol for shorter annealing times. Default is
        False.
    flux_biases: list[float] | None
        Custom flux bias offsets for each qubit in units of Φ₀ (flux quantum).
        List length must equal the number of qubits. Default is None.
    flux_drift_compensation: bool
        Whether to compensate for drift in qubit flux over time using real-time
        calibration data. Default is True.
    h_gain_schedule: list[tuple[float, float]] | None
        Schedule for h-gain during annealing as a list of (time, gain) pairs.
        Time is in normalized units [0, 1]. Default is None.
    initial_state: list[int] | None
        Starting state for the annealing process. List of {-1, +1} values with
        length equal to the number of qubits. Default is None.
    max_answers: int | None
        Maximum number of unique answer states to return. Must be ≤ num_reads.
        Default is None.
    num_reads: int
        Number of annealing cycles to perform. Must be positive integer.
        Default is 1.
    programming_thermalization: float | None
        Wait time after programming the QPU in microseconds to allow the system
        to thermalize. Default is None.
    readout_thermalization: float | None
        Wait time after each anneal before reading results in microseconds.
        Default is None.
    reduce_intersample_correlation: bool
        Whether to add delay between samples to reduce correlation between
        consecutive measurements. Default is False.
    reinitialize_state: bool | None
        Whether to reset to a new initial state between reads to reduce correlation.
        Default is None.
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
        return "QA"

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
