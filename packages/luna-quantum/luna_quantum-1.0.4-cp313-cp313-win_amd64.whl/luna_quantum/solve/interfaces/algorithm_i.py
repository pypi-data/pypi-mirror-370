from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from luna_quantum.aqm_overwrites.model import Model
from luna_quantum.solve.domain.solve_job import SolveJob
from luna_quantum.solve.interfaces.backend_i import IBackend

BACKEND_TYPE = TypeVar("BACKEND_TYPE", bound=IBackend)


class IAlgorithm(ABC, Generic[BACKEND_TYPE]):
    """
    Interface for an algorithm that performs solve tasks based on a given model.

    This interface defines the structure expected for any solver implementation
    that can solve model problems and return results in the form of a `SolveJob`.
    """

    @abstractmethod
    def run(
        self,
        model: Model | str,
        name: str | None = None,
        backend: BACKEND_TYPE | None = None,
        *args: Any | None,
        **kwargs: Any | None,
    ) -> SolveJob:
        """
        Solve the given model problem and return the resulting job.

        Parameters
        ----------
        model: Optimization
            An instance of the `Optimization` class representing the problem
            to be solved, including any constraints or objectives.
        name: Optional[str]
            If provided, the name of the job. Defaults to None.
        backend: Optional[BACKEND_TYPE]
            If provided, the backend to use for the solver. If no backend is provided,
            the default backend for the solver will be used.

        Returns
        -------
        SolveJob
            A `SolveJob` object representing the results of the solve_job process,
            including the solve_job state and related metadata.
        """
