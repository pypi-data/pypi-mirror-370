from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
    from luna_quantum.solve.domain.solve_job import SolveJob


class ISolveJobFetchUpdatesUseCase(ABC):
    """Interface for fetching updates for a solve job.

    Implementations of this interface must provide the logic for
    initializing with a client and fetching updates when called.

    Attributes
    ----------
    client : ILunaSolve
        The client used for interacting with the solve job update service.
    """

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, solve_job: SolveJob) -> None:
        """
        Abstract method for fetching updates for a solve job.

        The fetched data will update the provided solve job object.

        Parameters
        ----------
        solve_job : SolveJob
            The solve job for which updates are to be fetched.
        """
