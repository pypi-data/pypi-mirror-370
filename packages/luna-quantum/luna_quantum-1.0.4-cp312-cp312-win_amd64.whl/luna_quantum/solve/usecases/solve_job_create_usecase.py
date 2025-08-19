from typing import TYPE_CHECKING, Any

from luna_quantum.aqm_overwrites.model import Model
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.factories.usecase_factory import UseCaseFactory
from luna_quantum.solve.domain.abstract.luna_algorithm import LunaAlgorithm
from luna_quantum.solve.domain.abstract.qpu_token_backend import QpuTokenBackend
from luna_quantum.solve.domain.solve_job import SolveJob
from luna_quantum.solve.errors.model_metadata_missing_error import (
    ModelMetadataMissingError,
)
from luna_quantum.solve.interfaces.algorithm_i import BACKEND_TYPE
from luna_quantum.solve.interfaces.usecases.solve_job_create_usecase_i import (
    ISolveJobCreateUseCase,
)
from luna_quantum.util.log_utils import progress

if TYPE_CHECKING:
    from luna_quantum.client.schemas.solve_job import SolveJobSchema
    from luna_quantum.solve.domain.model_metadata import ModelMetadata
    from luna_quantum.solve.interfaces.usecases import IModelLoadByIdUseCase


class SolveJobCreateUseCase(ISolveJobCreateUseCase):
    """
    Create a solve job.

    This class is responsible for creating a job through a specified client interface.

    Attributes
    ----------
    client : ILunaSolve
        The client implementation used to handle the job creation process.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Scheduling solve job...")
    def __call__(
        self,
        model: Model | str,
        luna_solver: LunaAlgorithm[BACKEND_TYPE],
        backend: BACKEND_TYPE,
        name: str | None,
    ) -> SolveJob:
        """
        Solve a model using the specified solver.

        The function solves a given model using the provided LunaSolver instance. If a
        string is given as the model, it fetches the model's metadata using a use-case.
        If the model metadata is missing, an exception is raised. The function finally
        creates a solve job using the solver and model information and returns it.

        Parameters
        ----------
        model : Union[Model, str]
            The model to be solved. It can either be an instance of `Model` or a
            string representing the model ID.
        luna_solver : LunaAlgorithm
            The solver to be used for solving the model.
        name: Optional[str]
            The name of the solve job. Can be None.

        Returns
        -------
        SolveJob
            The job containing the results of the solving process.

        Raises
        ------
        ModelMetadataMissingError
            Raised when the metadata for the given model is missing.
        """
        metadata: ModelMetadata | None
        if isinstance(model, str):
            load_uc: IModelLoadByIdUseCase = UseCaseFactory.model_load_by_id(
                client=self.client
            )
            metadata = load_uc(model_id=model).metadata
        else:
            model.save_luna(client=self.client)
            metadata = model.metadata

        if not metadata:
            raise ModelMetadataMissingError

        if isinstance(model, str):
            model = Model.load_luna(model_id=model, client=self.client)

        solver_parameters: dict[str, Any] = luna_solver.model_dump()
        solver_parameters.update(backend.model_dump())

        qpu_tokens = None
        if isinstance(backend, QpuTokenBackend):
            qpu_tokens = backend.get_qpu_tokens()

        solve_job: SolveJobSchema = self.client.solve_job.create(
            model_id=metadata.id,
            solver_name=luna_solver.algorithm_name,
            solver_parameters=solver_parameters,
            provider=backend.provider,
            qpu_tokens=qpu_tokens,
            name=name,
        )
        sj = SolveJob.model_validate(solve_job.model_dump())

        sj.set_evaluation_model(model)

        return sj
