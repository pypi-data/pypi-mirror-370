from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.aqm_overwrites import Model
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
    from luna_quantum.solve.domain.solve_job import SolveJob


class IModelGetSolveJobUseCase(ABC):
    """Interface for obtaining and solving Model jobs."""

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, model: Model) -> list[SolveJob]:
        """
        Abstract function to retrieve list of SolveJob objects from a given client.

        Parameters
        ----------
        model : Model
            The model for which SolveJob objects are to be retrieved.

        Returns
        -------
        List[SolveJob]
            A list of SolveJob objects.
        """
