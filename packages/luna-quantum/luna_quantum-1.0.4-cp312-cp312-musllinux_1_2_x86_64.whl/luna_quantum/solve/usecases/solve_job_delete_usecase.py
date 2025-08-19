from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.interfaces.usecases.solve_job_delete_usecase_i import (
    ISolveJobDeleteUseCase,
)
from luna_quantum.util.log_utils import progress


class SolveJobDeleteUseCase(ISolveJobDeleteUseCase):
    """
    Delete a solve job through the provided client interface.

    Attributes
    ----------
    client : ILunaSolve
        Client implementing the `ILunaSolve` interface responsible for interacting
        with the solve service.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Deleting solve job...")
    def __call__(self, solve_job_id: str) -> None:
        """
        Delete a solve_job with the specified job ID.

        This callable method is used to delete a solve_job given its unique job
        identifier.

        Parameters
        ----------
        solve_job_id : str
            The unique identifier of the solve job to be deleted.

        """
        self.client.solve_job.delete(solve_job_id=solve_job_id)
