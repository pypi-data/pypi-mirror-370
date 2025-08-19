from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.aqm_overwrites import Model
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
    from luna_quantum.solve.domain.model_metadata import ModelMetadata


class IModelSaveUseCase(ABC):
    """Define an interface for handling Model saving use cases."""

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, model: Model) -> ModelMetadata:
        """
        Evaluate and retrieve metadata from an acquisition model.

        This abstract method is intended to be implemented to process a given
        acquisition model and derive specific metadata from it.

        Parameters
        ----------
        model : Model
            The acquisition model to be processed.

        Returns
        -------
        ModelMetadata
            The metadata derived from the acquisition model.
        """
