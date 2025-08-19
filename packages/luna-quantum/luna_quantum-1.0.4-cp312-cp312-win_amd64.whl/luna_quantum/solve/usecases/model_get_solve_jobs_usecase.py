from typing import TYPE_CHECKING

from luna_quantum.aqm_overwrites import Model
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.domain.solve_job import SolveJob
from luna_quantum.solve.interfaces.usecases.model_get_solve_jobs_usecase_i import (
    IModelGetSolveJobUseCase,
)
from luna_quantum.util.log_utils import progress

if TYPE_CHECKING:
    from luna_quantum.client.schemas.solve_job import SolveJobSchema


class ModelGetSolveJobsUseCase(IModelGetSolveJobUseCase):
    """
    Handle the retrieval of solve jobs for a given Model.

    This class is responsible for interacting with the client to fetch solve jobs
    related to a given Model. It ensures that the required metadata is present
    before performing operations with the client.

    Attributes
    ----------
    client : ILunaSolve
        The client used to communicate with the solve job backend or service.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Loading solve job...")
    def __call__(self, model: Model) -> list[SolveJob]:
        """
        Load solve jobs from the given Model instance.

        Fetches and validates all solve jobs associated with the given Model's
        metadata and returns them as a list of SolveJob objects. If metadata is
        missing in the Model, an empty list is returned.

        Parameters
        ----------
        model : Model
            The Model instance whose associated solve jobs are to be fetched.

        Returns
        -------
        List[SolveJob]
            A list of SolveJob objects derived from the fetched solve jobs..
        """
        if model.metadata is None:
            return []

        model_id = model.metadata.id

        solutions: list[SolveJobSchema] = self.client.solve_job.get_all(
            model_id=model_id
        )

        return [SolveJob.model_validate(s.model_dump()) for s in solutions]
