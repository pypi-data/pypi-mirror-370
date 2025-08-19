from typing import Any

from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.backends import DWaveQpu


class RepeatedReverseQuantumAnnealing(LunaAlgorithm[DWaveQpu]):
    """
    Parameters for the Repeated Reverse Quantum Annealing algorithm.

    This approach combines reverse annealing (starting from a classical state) with
    repetition to refine solutions iteratively. It's particularly useful for:
    1. Local refinement of solutions found by classical methods
    2. Escaping local minima by temporarily increasing quantum fluctuations
    3. Improving solutions through multiple rounds of quantum optimization

    The process involves:
    - Starting with classical initial states
    - Partially "unsolving" them by increasing quantum fluctuations
    - Re-annealing to find potentially better nearby solutions
    - Repeating with the best solutions found

    Attributes
    ----------
    anneal_offsets: Any | None
        Per-qubit time offsets for the annealing path, allowing qubits to anneal at
        different rates. Useful for problems with varying energy scales or when certain
        qubits need different annealing trajectories. Default is None, which uses
        standard annealing for all qubits.
    annealing_time: Any | None
        Duration of the annealing process in microseconds. Longer times can improve
        solution quality for problems with small energy gaps but increase runtime.
        Default is None, which uses the QPU's default annealing time.
    auto_scale: Any | None
        Whether to automatically normalize the problem energy range to match hardware
        capabilities, preventing precision issues in the physical implementation.
        Default is None, which uses the D-Wave system's default setting.
    flux_biases: Any | None
        Custom flux bias offsets for each qubit to compensate for manufacturing
        variations in the QPU hardware or to intentionally bias certain qubits.
        Default is None, using standard calibration values.
    flux_drift_compensation: bool
        Whether to compensate for drift in qubit flux over time, improving the
        reliability and consistency of results across multiple runs.
        Default is True, which is recommended for most applications.
    h_gain_schedule: Any | None
        Schedule for h-gain (linear coefficient strength) during annealing,
        allowing dynamic adjustment of problem coefficients throughout the process.
        Default is None, using standard gain settings.
    max_answers: int | None
        Maximum number of unique answer states to return from the quantum hardware.
        Useful for collecting diverse solutions while filtering out duplicates.
        Must be greater than or equal to 1 if specified. Default is None, which returns
        all unique solutions found.
    programming_thermalization: float | None
        Wait time (in microseconds) after programming the QPU, allowing it to
        reach thermal equilibrium before starting the annealing process.
        Must be positive if specified. Default is None, using system default.
    readout_thermalization: float | None
        Wait time (in microseconds) after each anneal before reading results.
        Helps ensure the qubits have settled into their final states before measurement.
        Must be positive if specified. Default is None, using system default.
    reduce_intersample_correlation: bool
        Whether to add delay between samples to reduce temporal correlations
        that might bias results across multiple runs. Default is False to minimize
        runtime, but can be set to True when sample independence is critical.
    initial_states: list[dict[str, int]] | None
        Initial classical states to start the reverse annealing from, specified as
        dictionaries mapping variable names to binary values (0 or 1). For each state,
        one call to the sampler with parameter `initial_state=state` will be made
        in the first iteration. Default is None, in which case random or specified
        states are generated according to n_initial_states.
    n_initial_states: int
        Number of initial states to create when `initial_states` is None.
        Controls the diversity of starting points for the algorithm.
        Ignored if `initial_states` is provided. Default is 1. Must be ≥1.
    samples_per_state: int
        How many samples to create per state in each iteration after the first.
        More samples increase the chance of finding improvements but use more QPU time.
        Controls the breadth of exploration around each promising solution.
        Default is 1. Must be ≥1.
    beta_schedule: list[float]
        Beta schedule controlling the quantum fluctuation strength during reverse
        annealing. Beta is the inverse temperature (1/T), with lower values allowing
        more thermal excitation to explore the energy landscape more widely.
        Default [0.5, 3] provides moderate initial fluctuation followed by cooling,
        balancing exploration and exploitation.
    timeout: float
        Maximum runtime in seconds before the solver stops, regardless of convergence.
        Provides a hard time limit to ensure the algorithm completes within a reasonable
        timeframe. Default is 300 seconds (5 minutes), balancing solution quality with
        timeliness.
    max_iter: int
        Maximum number of iterations (reverse annealing cycles) to perform.
        Each iteration refines the solutions from the previous round, potentially
        discovering better solutions in the neighborhood of good candidates.
        Default is 10, providing good refinement without excessive QPU usage.
    target: Any | None
        Target energy value that, if reached, causes the algorithm to terminate early.
        Allows for early stopping when a sufficiently good solution is found.
        Default is None (run until other stopping criteria are met).
    check_trivial: bool
        Whether to check for and handle trivial variables (those without interactions)
        before sending the problem to the QPU. Adds some computational overhead but
        prevents potential runtime errors and improves embedding efficiency.
        Default is True, which is recommended for robust operation.
    """

    anneal_offsets: Any | None = None
    annealing_time: Any | None = None
    auto_scale: Any | None = None
    flux_biases: Any | None = None
    flux_drift_compensation: bool = True
    h_gain_schedule: Any | None = None
    max_answers: int | None = Field(default=None, ge=1)
    programming_thermalization: float | None = Field(default=None, gt=0)
    readout_thermalization: float | None = Field(default=None, gt=0)
    reduce_intersample_correlation: bool = False

    initial_states: list[dict[str, int]] | None = None
    n_initial_states: int = Field(default=1, ge=1)
    samples_per_state: int = Field(default=1, ge=1)
    beta_schedule: list[float] = Field(default_factory=lambda: [0.5, 3])
    timeout: float = 300
    max_iter: int = 10
    target: Any | None = None
    check_trivial: bool = True

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
        return "RRQA"

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
