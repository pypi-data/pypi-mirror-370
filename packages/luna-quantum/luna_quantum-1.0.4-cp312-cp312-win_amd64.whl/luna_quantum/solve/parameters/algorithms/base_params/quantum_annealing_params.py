from pydantic import BaseModel, Field


class QuantumAnnealingParams(BaseModel):
    """
    Parameters for quantum annealing sampling on physical quantum processors (QPUs).

    These parameters control the quantum annealing process on hardware devices like
    D-Wave quantum annealers, specifying how the annealing is performed, how many
    samples to collect, and various hardware-specific settings that affect solution
    quality and runtime.

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

    anneal_offsets: list[float] | None = None
    anneal_schedule: list[tuple[float, float]] | None = None
    annealing_time: float | None = Field(default=None, gt=0)
    auto_scale: bool | None = None
    fast_anneal: bool = False
    flux_biases: list[float] | None = None
    flux_drift_compensation: bool = True
    h_gain_schedule: list[tuple[float, float]] | None = None

    initial_state: list[int] | None = None
    max_answers: int | None = Field(default=None, ge=1)
    num_reads: int = Field(default=1, ge=1)
    programming_thermalization: float | None = Field(default=None, gt=0)
    readout_thermalization: float | None = Field(default=None, gt=0)
    reduce_intersample_correlation: bool = False
    reinitialize_state: bool | None = None
