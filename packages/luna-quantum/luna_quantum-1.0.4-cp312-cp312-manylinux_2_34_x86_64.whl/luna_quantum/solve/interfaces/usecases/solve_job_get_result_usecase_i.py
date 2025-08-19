from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum import Solution
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
    from luna_quantum.client.schemas.enums.call_style import CallStyle
    from luna_quantum.solve.domain.solve_job import SolveJob


class ISolveJobGetResultUseCase(ABC):
    """
    Abstract base class for retrieving the solve job results.

    This class defines an interface for operations related to solve job result
    processing with specific parameters and behavior.

    Attributes
    ----------
    client : ILunaSolve
        The client responsible for interacting with the solve service.
    """

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(
        self,
        solve_job: SolveJob,
        sleep_time_max: float,
        sleep_time_increment: float,
        sleep_time_initial: float,
        call_style: CallStyle,
    ) -> Solution | None:
        """
        Callable method for retrieving the solve job results.

        Abstract method for solving a given job with customizable retry settings,
        including maximum sleep time, incremental sleep time adjustments, and
        initial sleep time. The call style can also be specified.

        Parameters
        ----------
        solve_job : SolveJob
            The job to be solved.
        sleep_time_max : float
            Maximum sleep time allowed between retries in seconds.
        sleep_time_increment : float
            Incremental value added to sleep time after each retry in seconds.
        sleep_time_initial : float
            Initial sleep time before the first retry in seconds.
        call_style : CallStyle
            The style in which the job solving is conducted.

        Returns
        -------
        Optional[Solution]
            The solution to the job if solving is successful, otherwise None.
        """
