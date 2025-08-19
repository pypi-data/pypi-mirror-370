from abc import abstractmethod
from logging import Logger
from typing import TYPE_CHECKING, Any, ClassVar, Generic

from pydantic import BaseModel, ConfigDict, Field, field_validator

from luna_quantum.aqm_overwrites.model import Model
from luna_quantum.client.controllers.luna_solve import LunaSolve
from luna_quantum.factories.luna_solve_client_factory import LunaSolveClientFactory
from luna_quantum.solve.domain.solve_job import SolveJob
from luna_quantum.solve.errors.incompatible_backend_error import (
    IncompatibleBackendError,
)
from luna_quantum.solve.interfaces.algorithm_i import BACKEND_TYPE, IAlgorithm
from luna_quantum.util.log_utils import Logging

if TYPE_CHECKING:
    from luna_quantum.solve.interfaces.usecases import ISolveJobCreateUseCase


class LunaAlgorithm(IAlgorithm[BACKEND_TYPE], BaseModel, Generic[BACKEND_TYPE]):
    """
    Class representing a solver for Luna model problems.

    This class serves as a base model combining functionality for model
    solvers, client management, and configurations needed for integrating with
    Luna's solving capabilities.
    """

    _logger: ClassVar[Logger] = Logging.get_logger(__name__)
    backend: BACKEND_TYPE | None = Field(
        default=None,
        exclude=True,
        repr=False,
    )

    @field_validator("backend", mode="before")
    @classmethod
    def backend_validator(cls, v: Any) -> BACKEND_TYPE | None:  # noqa: ANN401 # Ignore ANN401 here because the type for validation could be every type.
        """
        Validate and ensure the compatibility of the backend.

        Convert or validate the backend input to ensure compatibility with
        the expected backend type. This method is called before assigning a
        value to the backend attribute.

        Parameters
        ----------
        v : Any
            The value to be validated or converted into the compatible backend type.

        Returns
        -------
        Optional[BACKEND_TYPE]
            The validated or converted backend type. It returns None if the validation
            fails and no compatible backend type can be determined.

        Raises
        ------
        IncompatibleBackendError
            Raised if the value cannot be ensured to meet the backend compatibility
            requirements.
        """
        return cls._ensure_backend_compatibility(v)

    @classmethod
    def _ensure_backend_compatibility(cls, backend: Any) -> BACKEND_TYPE | None:  # noqa: ANN401 Disabled since we want to check every possible input if its valid
        """
        Ensure the compatibility of the provided backend.

        Check if the given backend is compatible with the current algorithm. If not,
        log an error and raise an exception. Return without any action if the
        backend is None.

        Parameters
        ----------
        backend : Optional[BACKEND_TYPE]
            Backend instance to be verified for compatibility.

        Raises
        ------
        IncompatibleBackendError
            If the backend is not compatible with the algorithm.
        """
        if backend is None:
            return None

        if not isinstance(backend, cls.get_compatible_backends()):
            cls._logger.error(
                f"Backend of type {type(backend)}"
                f" is not compatible with the '{cls.__name__}' Algorithm. "
                f"Use one of the following: {cls.get_compatible_backends()}",
            )
            raise IncompatibleBackendError(backend, cls)

        # We checked before if its a instance of BACKEND_TYPE
        # so we know here that this is correct,
        # unless we implement cls.get_compatible_backends() wrong.
        return backend

    def run(
        self,
        model: Model | str,
        name: str | None = None,
        backend: BACKEND_TYPE | None = None,
        client: LunaSolve | str | None = None,
        *args: Any,  # noqa: ARG002 its set here in case a child needs more set parameters
        **kwargs: Any,  # noqa: ARG002 its set here in case a child needs more set parameters
    ) -> SolveJob:
        """
        Run the configured solver.

        Parameters
        ----------
        model : Model or str
            The model to be optimized or solved. It could be an Model instance or
            a string identifier representing the model id.
        name: Optional[str]
            If provided, the name of the job. Defaults to None.
        backend: Optional[BACKEND_TYPE]
            Backend to use for the solver. If not provided, the default backend is
            used.
        client : LunaSolve or str, optional
            The client interface used to interact with the backend services. If
            not provided, a default client will be used.
        *args : Any
            Additional arguments that will be passed to the solver or client.
        **kwargs : Any
            Additional keyword parameters for configuration or customization.

        Returns
        -------
        SolveJob
            The job object containing the information about the solve process.
        """
        from luna_quantum.factories.usecase_factory import UseCaseFactory

        b: BACKEND_TYPE
        if backend is not None:
            b = backend
        elif self.backend is not None:
            b = self.backend
        else:
            b = self.get_default_backend()

        self._ensure_backend_compatibility(b)

        c = LunaSolveClientFactory.get_client(client=client)

        uc: ISolveJobCreateUseCase = UseCaseFactory.solve_job_create(client=c)

        return uc(model=model, luna_solver=self, backend=b, name=name)

    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """
        Returns the name of the algorithm.

        This abstract property method is intended to be overridden by subclasses.
        It should provide the name of the algorithm being implemented.

        Returns
        -------
        str
            The name of the algorithm.
        """

    @classmethod
    @abstractmethod
    def get_default_backend(cls) -> BACKEND_TYPE:
        """
        Return the default backend implementation.

        This property must be implemented by subclasses to provide
        the default backend instance to use when no specific backend
        is specified.

        Returns
        -------
            BACKEND_TYPE
                An instance of a class implementing the IBackend interface that serves
                as the default backend.
        """

    @classmethod
    @abstractmethod
    def get_compatible_backends(cls) -> tuple[type[BACKEND_TYPE], ...]:
        """
        Check at runtime if the used backend is compatible with the solver.

        Returns
        -------
        tuple[type[IBackend], ...]
            True if the backend is compatible with the solver, False otherwise.

        """

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra="allow",
        validate_assignment=True,
    )
