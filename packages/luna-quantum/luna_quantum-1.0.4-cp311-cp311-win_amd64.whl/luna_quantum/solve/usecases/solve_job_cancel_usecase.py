from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.domain.solve_job import SolveJob
from luna_quantum.solve.interfaces.usecases.solve_job_cancel_usecase_i import (
    ISolveJobCancelUseCase,
)
from luna_quantum.util.log_utils import progress
from luna_quantum.util.pydantic_utils import PydanticUtils


class SolveJobCancelUseCase(ISolveJobCancelUseCase):
    """
    Handles the cancellation of a solve job through the provided client.

    This class is responsible for interfacing with the given ILunaSolve client to
    cancel an existing solve job by utilizing its `solution.cancel` method. It
    validates and updates the solve job model after the cancellation.

    Attributes
    ----------
    client : ILunaSolve
        The client interface responsible for communicating with the backend
        solve services.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Canceling solve job...")
    def __call__(self, solve_job: SolveJob) -> None:
        """
        Call method to process a given SolveJob.

        This method interacts with an API client to process cancellation of a solution
        related to the input SolveJob, updates the SolveJob model, and modifies it
        using updated data.

        Parameters
        ----------
        solve_job : SolveJob
            The job instance that needs to be processed, updated, and validated.

        Returns
        -------
        None
        """
        solve_job_schema = self.client.solve_job.cancel(solve_job_id=solve_job.id)

        updated_solve_job = SolveJob.model_validate(solve_job_schema.model_dump())
        PydanticUtils.update_model(solve_job, updated_solve_job)
