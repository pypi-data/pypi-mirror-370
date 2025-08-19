from luna_quantum._core import Solution
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.client.schemas.enums.call_style import CallStyle
from luna_quantum.client.schemas.enums.status import StatusEnum
from luna_quantum.solve.domain.solve_job import SolveJob
from luna_quantum.solve.interfaces.usecases.solve_job_get_result_usecase_i import (
    ISolveJobGetResultUseCase,
)
from luna_quantum.util.active_waiting import ActiveWaiting
from luna_quantum.util.log_utils import Logging, progress


class SolveJobGetResultUseCase(ISolveJobGetResultUseCase):
    """
    Handle the process of retrieving and interacting with a solve job's result.

    This class interacts with a backend client to manage fetching and handling
    results for a solve job, using different strategies for waiting and polling
    depending on the specified call style.

    Attributes
    ----------
    client : ILunaSolve
        Client used to interact with the solve job and retrieve its results.
    """

    client: ILunaSolve
    logger = Logging.get_logger(__name__)

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Retrieving solve job...")
    def __call__(
        self,
        solve_job: SolveJob,
        sleep_time_max: float,
        sleep_time_increment: float,
        sleep_time_initial: float,
        call_style: CallStyle,
    ) -> Solution | None:
        """
        Execute the given solve job with specified waiting strategy.

        Parameters
        ----------
        solve_job : SolveJob
            The job that needs to be solved.
        sleep_time_max : float
            The maximum amount of time to wait between checks.
        sleep_time_increment : float
            The incremental step to increase sleep time during active waiting.
        sleep_time_initial : float
            The initial sleep time for the waiting strategy.
        call_style : CallStyle
            The style of waiting (e.g., active waiting) to use when processing the job.

        Returns
        -------
        Optional[Solution]
            The solution for the given solve job if successfully processed, otherwise
            None.
        """
        if call_style is CallStyle.ACTIVE_WAITING:
            final_states = StatusEnum.CANCELED, StatusEnum.DONE, StatusEnum.FAILED

            ActiveWaiting.run(
                loop_check=lambda: solve_job.get_status(
                    client=self.client, status_source="remote"
                )
                not in final_states,
                loop_call=None,
                sleep_time_max=sleep_time_max,
                sleep_time_increment=sleep_time_increment,
                sleep_time_initial=sleep_time_initial,
            )
        try:
            if solve_job.status == StatusEnum.CANCELED:
                self.logger.warning(
                    "Solve job is cancelled. Result cannot be retrieved."
                )
                return None
            if solve_job.status == StatusEnum.FAILED:
                self.logger.error(
                    f"Solve job failed with the error '{solve_job.error_message}'."
                )
                return None
            aq_solution: Solution = self.client.solve_job.get_solution(
                solve_job_id=solve_job.id
            )
        except Exception:
            # TODO(Llewellyn) more fine grained exception handling # noqa: FIX002, TD004
            return None

        return aq_solution
