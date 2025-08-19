from typing import Literal

from pydantic import Field

from luna_quantum.solve.domain.abstract import LunaAlgorithm
from luna_quantum.solve.parameters.backends import DWaveQpu
from luna_quantum.solve.parameters.constants import DEFAULT_ATOL, DEFAULT_RTOL


class QAGA(LunaAlgorithm[DWaveQpu]):
    """
    Parameters for the Quantum Assisted Genetic Algorithm (QAGA).

    QAGA combines quantum computing with genetic algorithms to enhance the search for
    optimal solutions. It uses quantum annealing for mutation and recombination
    operations, potentially allowing the algorithm to escape local optima more
    effectively than classical genetic algorithms.

    The algorithm maintains a population of candidate solutions that evolve through
    selection, quantum-enhanced recombination, and mutation operations across
    generations.

    Attributes
    ----------
    p_size : int
        Initial population size (number of candidate solutions). Larger populations
        provide more diversity but require more computation. Default is 20, suitable
        for small to medium problems.
    p_inc_num : int
        Number of new individuals added to the population after each generation.
        Controls population growth rate. Default is 5, allowing moderate expansion.
    p_max : int | None
        Maximum population size. Once reached, no more growth occurs. Prevents
        unbounded population expansion. Default is 160, balancing diversity with
        computational cost.
    pct_random_states : float
        Percentage of random states added to the population after each iteration.
        Helps maintain diversity and avoid premature convergence. Default is 0.25 (25%).
    mut_rate : float
        Mutation rate - probability to mutate an individual after each iteration.
        Higher values favor exploration, lower values favor exploitation.
        Default is 0.5, balanced between the two. Must be between 0.0 and 1.0.
    rec_rate : int
        Recombination rate - number of mates each individual is recombined with
        per generation. Higher values increase genetic mixing. Default is 1.
    rec_method : Literal["cluster_moves", "one_point_crossover", "random_crossover"]
        Method used for recombining individuals:
        - "cluster_moves": Swaps clusters of related variables between solutions
        - "one_point_crossover": Splits solutions at a random point and exchanges parts
        - "random_crossover": Randomly exchanges bits between parents
        Default is "random_crossover", which provides good exploration.
    select_method : Literal["simple", "shared_energy"]
        Selection strategy for the next generation:
        - "simple": Pure energy-based selection
        - "shared_energy": Promotes diversity by penalizing similar solutions
        Default is "simple", focusing on solution quality.
    target : float | None
        Target energy level to stop the algorithm. If None, runs until other criteria
        are met. Default is None.
    atol : float
        Absolute tolerance when comparing energies to target. Default is 0.0.
    rtol : float
        Relative tolerance when comparing energies to target. Default is 0.0.
    timeout : float
        Maximum runtime in seconds. Includes preprocessing, network overhead, and
        quantum processing time. Default is 60.0 seconds.
    max_iter : Union[int, None]
        Maximum number of generations before stopping. None means no limit.
        Default is 100 generations.
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
        return "QAGA+"

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
