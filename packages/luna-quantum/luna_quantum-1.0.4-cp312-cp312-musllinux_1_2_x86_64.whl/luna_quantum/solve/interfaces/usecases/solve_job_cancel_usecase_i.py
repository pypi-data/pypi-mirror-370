from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
    from luna_quantum.solve.domain.solve_job import SolveJob


class ISolveJobCancelUseCase(ABC):
    """
    Represent an abstract base for solving job cancellation use case.

    This class defines the structure for a use case that allows canceling of solve
    jobs. It acts as an interface specifying methods to be implemented by
    concrete subclasses.
    """

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, solve_job: SolveJob) -> None:
        """
        Represent an abstract base for callable objects handling solve jobs.

        Parameters
        ----------
        solve_job : SolveJob
            The input job to process or solve.
        """
