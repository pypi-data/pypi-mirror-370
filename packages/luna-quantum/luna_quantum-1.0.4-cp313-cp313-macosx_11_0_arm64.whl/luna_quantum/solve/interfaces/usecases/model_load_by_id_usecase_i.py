from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.aqm_overwrites import Model
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve


class IModelLoadByIdUseCase(ABC):
    """Interface for loading an AQ Model by its ID."""

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, model_id: str) -> Model:
        """
        Abstract method that retrieves a model instance by its identifier.

        Parameters
        ----------
        model_id : str
            A unique identifier of the model to be retrieved.

        Returns
        -------
        Model
            The model instance corresponding to the given identifier.
        """
