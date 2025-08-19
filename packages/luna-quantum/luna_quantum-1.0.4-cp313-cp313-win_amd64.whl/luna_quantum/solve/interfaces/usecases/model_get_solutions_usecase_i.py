from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum import Model, Solution
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve


class IModelGetSolutionUseCase(ABC):
    """Interface to retrieve solutions for a specific Model."""

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, model: Model) -> list[Solution]:
        """
        Abstract method to retrieve solutions for a specific Model.

        Parameters
        ----------
        model : Model
            The model to be processed.

        Returns
        -------
        list[Solution]
            A list of solutions generated after processing the query model.

        """
