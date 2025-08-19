from typing import Literal

from pydantic import BaseModel, Field


class FujitsuV2Mixin(BaseModel):
    """
    FujitsuV2Mixin.

    Parameters for V2 optimization algorithms, particularly relevant for
    Digital Annealer implementations.

    This class defines parameters controlling the annealing process, temperature
    scheduling, and solution mode for V2 solvers. These parameters impact how
    the algorithm traverses the energy landscape and converges to solutions.

    Attributes
    ----------
    optimization_method: Literal["annealing", "parallel_tempering"]
        Algorithm to use for optimization:
        - "annealing": Standard simulated annealing with gradual cooling
        - "parallel_tempering": Simultaneous runs at different temperatures with
          periodic state exchanges, effective for complex energy landscapes
        Default is "annealing".
    temperature_start: float
        Initial temperature for the annealing process. Higher values enable more
        exploration initially. Default is 1000.0. Range: [0.0, 1e20].
    temperature_end: float
        Final temperature for the annealing process. Lower values enforce more
        exploitation in final phases. Default is 1.0. Range: [0.0, 1e20].
    temperature_mode: int
        Cooling curve mode for temperature decay:
        - 0: Exponential cooling - reduce by factor at fixed intervals
        - 1: Inverse cooling - faster initial cooling, slower later
        - 2: Inverse root cooling - another non-linear cooling schedule
        Default is 0 (exponential).
    temperature_interval: int
        Number of iterations between temperature adjustments. Larger values
        allow more exploration at each temperature. Default is 100. Range: [1, 1e20].
    offset_increase_rate: float
        Rate at which dynamic offset increases when no bit is selected.
        Helps escape plateaus in the energy landscape. Default is 5.0.
        Range: [0.0, 1e20].
    solution_mode: Literal["QUICK", "COMPLETE"]
        Determines solution reporting strategy:
        - "QUICK": Return only the overall best solution (faster)
        - "COMPLETE": Return best solutions from all runs (more diverse)
        Default is "COMPLETE", providing more solution options.
    flip_probabilities: Tuple[float, float]
        Probabilities used for determining temperature parameters.
        First value is probability of accepting worse solutions at start temperature,
        second value is probability at end temperature. Default is (0.99, 0.01).
    annealing_steps: Tuple[float, float]
        Portion of annealing trajectory where end_progress_probability is reached.
        Controls the annealing schedule shape. Default is (0.0, 0.5).
    sampling_runs: int
        Number of random walkers used for energy delta determination during
        parameter estimation sampling. Default is 100.
    """

    optimization_method: Literal["annealing", "parallel_tempering"] = "annealing"
    temperature_start: float = Field(default=1_000.0, ge=0.0, le=1e20)
    temperature_end: float = Field(default=1.0, ge=0.0, le=1e20)
    temperature_mode: int = 0
    temperature_interval: int = Field(default=100, ge=1, le=int(1e20))
    offset_increase_rate: float = Field(default=5.0, ge=0.0, le=1e20)
    solution_mode: Literal["QUICK", "COMPLETE"] = "COMPLETE"
    flip_probabilities: tuple[float, float] = 0.99, 0.01
    annealing_steps: tuple[float, float] = 0.0, 0.5
    sampling_runs: int = 100
