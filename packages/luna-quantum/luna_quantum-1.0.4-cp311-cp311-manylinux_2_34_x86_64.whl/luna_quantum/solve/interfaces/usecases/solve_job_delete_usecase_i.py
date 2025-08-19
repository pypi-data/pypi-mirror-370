from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve


class ISolveJobDeleteUseCase(ABC):
    """Defines an abstract interface for deleting a Solve Job."""

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, solve_job_id: str) -> None:
        """
        Abstract method for deleting a Solve Job.

        Parameters
        ----------
        solve_job_id : str
            Unique identifier for the solve job to process.

        Returns
        -------
        Model
            The Model instance that corresponds to the processed job.

        """
