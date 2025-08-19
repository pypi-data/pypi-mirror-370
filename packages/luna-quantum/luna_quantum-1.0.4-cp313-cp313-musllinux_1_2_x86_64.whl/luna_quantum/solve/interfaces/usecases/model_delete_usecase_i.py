from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.aqm_overwrites import Model
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve


class IModelDeleteUseCase(ABC):
    """Interface for deleting a models."""

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, model: Model) -> None:
        """
        Abstract method for deleting a model.

        Parameters
        ----------
        model : Model
            Model to be deleted.
        """
