from typing import Literal

from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.backends import DWave
from luna_quantum.solve.parameters.constants import DEFAULT_ATOL, DEFAULT_RTOL


class SAGA(LunaAlgorithm[DWave]):
    """
    Simulated Annealing Genetic Algorithm (SAGA).

    SAGA combines genetic algorithms with simulated annealing to enhance optimization.
    While QAGA uses quantum annealing, SAGA uses classical simulated annealing for the
    mutation and recombination operations, making it more accessible while still
    providing benefits over standard genetic algorithms.

    The algorithm maintains a population of solutions that evolve through selection,
    annealing-enhanced recombination, and mutation operations across generations.

    Attributes
    ----------
    p_size : int
        Initial population size (number of candidate solutions). Default is 20.
    p_inc_num : int
        Number of new individuals added to the population after each generation.
        Default is 5.
    p_max : int | None
        Maximum population size. Once reached, no more growth occurs.
        Default is 160.
    pct_random_states : float
        Percentage of random states added to the population after each iteration.
        Default is 0.25 (25%).
    mut_rate : float
        Mutation rate - probability to mutate an individual after each iteration.
        Default is 0.5. Must be between 0.0 and 1.0.
    rec_rate : int
        Recombination rate - number of mates each individual is recombined with
        per generation. Default is 1.
    rec_method : Literal["cluster_moves", "one_point_crossover", "random_crossover"]
        Method used for recombining individuals. Default is "random_crossover".
    select_method : Literal["simple", "shared_energy"]
        Selection strategy for the next generation. Default is "simple".
    target : Union[float, None]
        Target energy level to stop the algorithm. Default is None.
    atol : float
        Absolute tolerance when comparing energies to target.
        Default is DEFAULT_ATOL.
    rtol : float
        Relative tolerance when comparing energies to target.
        Default is DEFAULT_RTOL.
    timeout : float
        Maximum runtime in seconds. Default is 60.0 seconds.
    max_iter : int | None
        Maximum number of generations before stopping. Default is 100.
    num_sweeps: int
        Initial number of sweeps for simulated annealing in the first iteration.
        Default is 10.
    num_sweeps_inc_factor: float
        Factor by which to increase num_sweeps after each iteration.
        Default is 1.2 (20% increase per iteration).
    num_sweeps_inc_max: Optional[int]
        Maximum number of sweeps that may be reached when increasing the num_sweeps.
        Default is 7,000.
    beta_range_type: Literal["default", "percent", "fixed", "inc"]
        Method used to compute the temperature range (beta range) for annealing.
        Default is "default".
    beta_range: Optional[Tuple[float, float]]
        Explicit beta range (inverse temperature) used with beta_range_type "fixed" or
        "percent". Default is None.
    """

    p_size: int = 20
    p_inc_num: int = 5
    p_max: int | None = 160
    pct_random_states: float = 0.25
    mut_rate: float = Field(default=0.5, ge=0.0, le=1.0)
    rec_rate: int = 1
    rec_method: Literal["cluster_moves", "one_point_crossover", "random_crossover"] = (
        "random_crossover"
    )
    select_method: Literal["simple", "shared_energy"] = "simple"
    target: float | None = None
    atol: float = DEFAULT_ATOL
    rtol: float = DEFAULT_RTOL
    timeout: float = 60.0
    max_iter: int | None = 100

    num_sweeps: int = 10
    num_sweeps_inc_factor: float = 1.2
    num_sweeps_inc_max: int | None = 7_000
    beta_range_type: Literal["default", "percent", "fixed", "inc"] = "default"
    beta_range: tuple[float, float] | None = None

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
        return "SAGA+"

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
