from typing import ClassVar

from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.interfaces.usecases import (
    IModelLoadMetadataByHashUseCase,
)
from luna_quantum.solve.interfaces.usecases.model_delete_usecase_i import (
    IModelDeleteUseCase,
)
from luna_quantum.solve.interfaces.usecases.model_fetch_metadata_usecase_i import (
    IModelFetchMetadataUseCase,
)
from luna_quantum.solve.interfaces.usecases.model_get_solutions_usecase_i import (
    IModelGetSolutionUseCase,
)
from luna_quantum.solve.interfaces.usecases.model_get_solve_jobs_usecase_i import (
    IModelGetSolveJobUseCase,
)
from luna_quantum.solve.interfaces.usecases.model_load_by_id_usecase_i import (
    IModelLoadByIdUseCase,
)
from luna_quantum.solve.interfaces.usecases.model_load_by_metadata_usecase_i import (
    IModelLoadByMetadataUseCase,
)
from luna_quantum.solve.interfaces.usecases.model_save_usecase_i import (
    IModelSaveUseCase,
)
from luna_quantum.solve.interfaces.usecases.solve_job_cancel_usecase_i import (
    ISolveJobCancelUseCase,
)
from luna_quantum.solve.interfaces.usecases.solve_job_create_usecase_i import (
    ISolveJobCreateUseCase,
)
from luna_quantum.solve.interfaces.usecases.solve_job_delete_usecase_i import (
    ISolveJobDeleteUseCase,
)
from luna_quantum.solve.interfaces.usecases.solve_job_fetch_updates_usecase_i import (
    ISolveJobFetchUpdatesUseCase,
)
from luna_quantum.solve.interfaces.usecases.solve_job_get_result_usecase_i import (
    ISolveJobGetResultUseCase,
)


class UseCaseFactory:
    """
    Factory class to manage use-case implementations.

    This class provides methods to manage and configure use-case classes for various
    model and solve job operations.
    """

    _model_fetch_class: ClassVar[type[IModelFetchMetadataUseCase]]
    _model_delete_class: ClassVar[type[IModelDeleteUseCase]]
    _model_get_solution_class: ClassVar[type[IModelGetSolutionUseCase]]
    _model_get_solve_job_class: ClassVar[type[IModelGetSolveJobUseCase]]
    _model_load_by_id_class: ClassVar[type[IModelLoadByIdUseCase]]
    _model_load_by_hash_class: ClassVar[type[IModelLoadMetadataByHashUseCase]]
    _model_load_by_metadata_class: ClassVar[type[IModelLoadByMetadataUseCase]]
    _model_save_class: ClassVar[type[IModelSaveUseCase]]

    _solve_job_cancel_class: ClassVar[type[ISolveJobCancelUseCase]]
    _solve_job_create_class: ClassVar[type[ISolveJobCreateUseCase]]
    _solve_job_delete_class: ClassVar[type[ISolveJobDeleteUseCase]]
    _solve_job_get_result_class: ClassVar[type[ISolveJobGetResultUseCase]]
    _solve_job_fetch_updates_class: ClassVar[type[ISolveJobFetchUpdatesUseCase]]

    @classmethod
    def set_model_fetch_class(
        cls, model_fetch_class: type[IModelFetchMetadataUseCase]
    ) -> None:
        """Set the implementation class for model fetch operations.

        Parameters
        ----------
        model_fetch_class : Type[IModelFetchMetadataUseCase]
            The class implementing IModelFetchMetadataUseCase
        """
        cls._model_fetch_class = model_fetch_class

    @classmethod
    def set_model_delete_class(
        cls, model_delete_class: type[IModelDeleteUseCase]
    ) -> None:
        """Set the implementation class for model delete operations.

        Parameters
        ----------
        model_delete_class : Type[IModelDeleteUseCase]
            The class implementing IModelDeleteUseCase
        """
        cls._model_delete_class = model_delete_class

    @classmethod
    def set_model_get_solution_class(
        cls, model_get_solution_class: type[IModelGetSolutionUseCase]
    ) -> None:
        """Set the implementation class for getting model solutions.

        Parameters
        ----------
        model_get_solution_class : Type[IModelGetSolutionUseCase]
            The class implementing IModelGetSolutionUseCase
        """
        cls._model_get_solution_class = model_get_solution_class

    @classmethod
    def set_model_get_solve_job_class(
        cls, model_get_solve_job_class: type[IModelGetSolveJobUseCase]
    ) -> None:
        """Set the implementation class for getting model solve jobs.

        Parameters
        ----------
        model_get_solve_job_class : Type[IModelGetSolveJobUseCase]
            The class implementing IModelGetSolveJobUseCase
        """
        cls._model_get_solve_job_class = model_get_solve_job_class

    @classmethod
    def set_model_load_by_id_class(
        cls, model_load_by_id_class: type[IModelLoadByIdUseCase]
    ) -> None:
        """Set the implementation class for loading models by ID.

        Parameters
        ----------
        model_load_by_id_class : Type[IModelLoadByIdUseCase]
            The class implementing IModelLoadByIdUseCase
        """
        cls._model_load_by_id_class = model_load_by_id_class

    @classmethod
    def set_model_load_by_hash_class(
        cls, model_load_by_hash_class: type[IModelLoadMetadataByHashUseCase]
    ) -> None:
        """Set the implementation class for loading model metadata by hash.

        Parameters
        ----------
        model_load_by_hash_class : Type[IModelLoadMetadataByHashUseCase]
            The class implementing IModelLoadMetadataByHashUseCase
        """
        cls._model_load_by_hash_class = model_load_by_hash_class

    @classmethod
    def set_model_load_by_metadata_class(
        cls, model_load_by_metadata_class: type[IModelLoadByMetadataUseCase]
    ) -> None:
        """Set the implementation class for loading models by metadata.

        Parameters
        ----------
        model_load_by_metadata_class : Type[IModelLoadByMetadataUseCase]
            The class implementing IModelLoadByMetadataUseCase
        """
        cls._model_load_by_metadata_class = model_load_by_metadata_class

    @classmethod
    def set_model_save_class(cls, model_save_class: type[IModelSaveUseCase]) -> None:
        """Set the implementation class for saving models.

        Parameters
        ----------
        model_save_class : Type[IModelSaveUseCase]
            The class implementing IModelSaveUseCase
        """
        cls._model_save_class = model_save_class

    @classmethod
    def set_solve_job_cancel_class(
        cls, solve_job_cancel_class: type[ISolveJobCancelUseCase]
    ) -> None:
        """Set the implementation class for canceling solve jobs.

        Parameters
        ----------
        solve_job_cancel_class : Type[ISolveJobCancelUseCase]
            The class implementing ISolveJobCancelUseCase
        """
        cls._solve_job_cancel_class = solve_job_cancel_class

    @classmethod
    def set_solve_job_create_class(
        cls, solve_job_create_class: type[ISolveJobCreateUseCase]
    ) -> None:
        """Set the implementation class for creating solve jobs.

        Parameters
        ----------
        solve_job_create_class : Type[ISolveJobCreateUseCase]
            The class implementing ISolveJobCreateUseCase
        """
        cls._solve_job_create_class = solve_job_create_class

    @classmethod
    def set_solve_job_delete_class(
        cls, solve_job_delete_class: type[ISolveJobDeleteUseCase]
    ) -> None:
        """Set the implementation class for deleting solve jobs.

        Parameters
        ----------
        solve_job_delete_class : Type[ISolveJobDeleteUseCase]
            The class implementing ISolveJobDeleteUseCase
        """
        cls._solve_job_delete_class = solve_job_delete_class

    @classmethod
    def set_solve_job_get_result_class(
        cls, solve_job_get_result_class: type[ISolveJobGetResultUseCase]
    ) -> None:
        """Set the implementation class for getting solve job results.

        Parameters
        ----------
        solve_job_get_result_class : Type[ISolveJobGetResultUseCase]
            The class implementing ISolveJobGetResultUseCase
        """
        cls._solve_job_get_result_class = solve_job_get_result_class

    @classmethod
    def set_solve_job_fetch_updates_class(
        cls, solve_job_fetch_updates_class: type[ISolveJobFetchUpdatesUseCase]
    ) -> None:
        """Set the implementation class for fetching solve job updates.

        Parameters
        ----------
        solve_job_fetch_updates_class : Type[ISolveJobFetchUpdatesUseCase]
            The class implementing ISolveJobFetchUpdatesUseCase
        """
        cls._solve_job_fetch_updates_class = solve_job_fetch_updates_class

    @classmethod
    def model_load_by_id(cls, client: ILunaSolve) -> IModelLoadByIdUseCase:
        """
        Get the use-case to load a model using its ID.

        Parameters
        ----------
        client : ILunaSolve
            The client used to load the model by its ID.

        Returns
        -------
        IModelLoadByIdUseCase
            An instance of the model loaded by ID.
        """
        return cls._model_load_by_id_class(client=client)

    @classmethod
    def model_load_by_metadata(cls, client: ILunaSolve) -> IModelLoadByMetadataUseCase:
        """
        Get the use-case to load a model using metadata.

        Parameters
        ----------
        client : ILunaSolve
            The client interface used to load the model by metadata.

        Returns
        -------
        IModelLoadByMetadataUseCase
            The instance to handle model loading by metadata.
        """
        return cls._model_load_by_metadata_class(client=client)

    @classmethod
    def model_save(cls, client: ILunaSolve) -> IModelSaveUseCase:
        """
        Get the use-case to save the model using the specified client.

        Parameters
        ----------
        client : ILunaSolve
            The client used for performing the model save operation.

        Returns
        -------
        IModelSaveUseCase
            An instance of the class responsible for handling model save use cases.

        """
        return cls._model_save_class(client=client)

    @classmethod
    def model_fetch(cls, client: ILunaSolve) -> IModelFetchMetadataUseCase:
        """
        Get the use-case to fetch model metadata.

        Parameters
        ----------
        client : ILunaSolve
            The client used to fetch the metadata of the model.

        Returns
        -------
        IModelFetchMetadataUseCase
            An instance of the class responsible for fetching model metadata.
        """
        return cls._model_fetch_class(client=client)

    @classmethod
    def model_delete(cls, client: ILunaSolve) -> IModelDeleteUseCase:
        """
        Get the use-case to delete a model.

        Parameters
        ----------
        client : ILunaSolve
            The client used to delete the model.

        Returns
        -------
        IModelDeleteUseCase
            An instance of the class responsible for deleting models.
        """
        return cls._model_delete_class(client=client)

    @classmethod
    def model_get_solution(cls, client: ILunaSolve) -> IModelGetSolutionUseCase:
        """
        Get the use-case to retrieve solutions for a model.

        Parameters
        ----------
        client : ILunaSolve
            The client used to fetch solutions for the model.

        Returns
        -------
        IModelGetSolutionUseCase
            An instance of the class responsible for retrieving solutions.
        """
        return cls._model_get_solution_class(client=client)

    @classmethod
    def model_get_solve_job(cls, client: ILunaSolve) -> IModelGetSolveJobUseCase:
        """
        Get the use-case to retrieve solve jobs of a model.

        Parameters
        ----------
        client : ILunaSolve
            The client used to get the solve jobs of the model.

        Returns
        -------
        IModelGetSolveJobUseCase
            An instance of the class responsible for retrieving solve jobs.
        """
        return cls._model_get_solve_job_class(client=client)

    @classmethod
    def solve_job_cancel(cls, client: ILunaSolve) -> ISolveJobCancelUseCase:
        """
        Get the use-case to cancel a solve job.

        Parameters
        ----------
        client : ILunaSolve
            The client used to cancel a solve job.

        Returns
        -------
        ISolveJobCancelUseCase
            An instance of the class responsible for canceling solve jobs.
        """
        return cls._solve_job_cancel_class(client=client)

    @classmethod
    def solve_job_create(cls, client: ILunaSolve) -> ISolveJobCreateUseCase:
        """
        Get the use-case to create a new solve job.

        Parameters
        ----------
        client : ILunaSolve
            The client used to create a new solve job.

        Returns
        -------
        ISolveJobCreateUseCase
            An instance of the class responsible for creating solve jobs.
        """
        return cls._solve_job_create_class(client=client)

    @classmethod
    def solve_job_delete(cls, client: ILunaSolve) -> ISolveJobDeleteUseCase:
        """
        Get the use-case to delete a solve job.

        Parameters
        ----------
        client : ILunaSolve
            The client used to delete a solve job.

        Returns
        -------
        ISolveJobDeleteUseCase
            An instance of the class responsible for deleting solve jobs.
        """
        return cls._solve_job_delete_class(client=client)

    @classmethod
    def solve_job_get_result(cls, client: ILunaSolve) -> ISolveJobGetResultUseCase:
        """
        Get the use-case to fetch results of a solve job.

        Parameters
        ----------
        client : ILunaSolve
            The client used to fetch results of the solve job.

        Returns
        -------
        ISolveJobGetResultUseCase
            An instance of the class responsible for fetching solve job results.
        """
        return cls._solve_job_get_result_class(client=client)

    @classmethod
    def solve_job_fetch_update(cls, client: ILunaSolve) -> ISolveJobFetchUpdatesUseCase:
        """
        Get the use-case to fetch updates for a solve job.

        Parameters
        ----------
        client : ILunaSolve
            The client used to fetch updates for a solve job.

        Returns
        -------
        ISolveJobFetchUpdatesUseCase
            An instance of the class responsible for fetching solve job updates.
        """
        return cls._solve_job_fetch_updates_class(client=client)

    @classmethod
    def model_load_metadata_by_hash(
        cls, client: ILunaSolve
    ) -> IModelLoadMetadataByHashUseCase:
        """
        Get the use-case to load model metadata by its hash.

        Parameters
        ----------
        client : ILunaSolve
            The client used to load model metadata using a hash.

        Returns
        -------
        IModelLoadMetadataByHashUseCase
            An instance of the class responsible for loading model metadata by hash.
        """
        return cls._model_load_by_hash_class(client=client)
