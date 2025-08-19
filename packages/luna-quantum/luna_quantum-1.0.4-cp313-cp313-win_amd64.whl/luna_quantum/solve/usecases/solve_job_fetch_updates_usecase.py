from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.domain.solve_job import SolveJob
from luna_quantum.solve.interfaces.usecases.solve_job_fetch_updates_usecase_i import (
    ISolveJobFetchUpdatesUseCase,
)
from luna_quantum.util.log_utils import progress
from luna_quantum.util.pydantic_utils import PydanticUtils


class SolveJobFetchUpdatesUseCase(ISolveJobFetchUpdatesUseCase):
    """
    Fetches and applies updates to a solve job using a client.

    This class is responsible for retrieving the latest updates for a solve job
    from the client and applying them to the given solve job instance.

    Attributes
    ----------
    client : ILunaSolve
        Client used to fetch updates for solve jobs.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Fetching solve job...")
    def __call__(self, solve_job: SolveJob) -> None:
        """
        Execute fetch the updates of a specific `SolveJob` instance.

        This callable validates and updates a `SolveJob` instance using data fetched
        from the client. The fetched data is used to synchronize the job model with
        the server's definition.

        Parameters
        ----------
        solve_job : SolveJob
            The job to be processed, validated, and updated.

        Returns
        -------
        None
        """
        solve_job_schema = self.client.solve_job.get(solve_job_id=solve_job.id)
        solve_job_updated = SolveJob.model_validate(solve_job_schema.model_dump())

        PydanticUtils.update_model(solve_job, solve_job_updated)
