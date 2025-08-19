from luna_quantum._core import Solution
from luna_quantum.aqm_overwrites import Model
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.client.schemas.enums.status import StatusEnum
from luna_quantum.solve.interfaces.usecases.model_get_solutions_usecase_i import (
    IModelGetSolutionUseCase,
)
from luna_quantum.util.log_utils import progress


class ModelGetSolutionUseCase(IModelGetSolutionUseCase):
    """
    Use case for retrieving solutions of a model.

    Handles the process of interacting with the client to get all solutions
    for a specific AQ model based on its metadata and associated ID.

    Attributes
    ----------
    client : ILunaSolve
        The client responsible for fetching solutions from the external source.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Loading solution...")
    def __call__(self, model: Model) -> list[Solution]:
        """
        Load solutions of the given Model input.

        This function retrieves and returns a list of ISolution instances for the
        given Model. If the Model does not have metadata, an empty list is returned.

        Parameters
        ----------
        model : Model
            The input Model object whose associated solutions are to be retrieved.

        Returns
        -------
        list[Solution]
            A list of Solution objects associated with the given Model.
        """
        if model.metadata is None:
            return []

        model_id = model.metadata.id

        solve_jobs = self.client.solve_job.get_all(model_id=model_id)

        # TODO THIS IS SUPER INEFFICIENT  # noqa: FIX002, TD002, TD004
        return [
            self.client.solve_job.get_solution(solve_job_id=s.id)
            for s in solve_jobs
            if s.status is StatusEnum.DONE
        ]
