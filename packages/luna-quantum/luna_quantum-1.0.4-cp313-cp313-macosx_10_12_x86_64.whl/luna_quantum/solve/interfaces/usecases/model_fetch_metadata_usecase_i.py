from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.aqm_overwrites import Model
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
    from luna_quantum.solve.domain.model_metadata import ModelMetadata


class IModelFetchMetadataUseCase(ABC):
    """Abstract base class for fetching metadata of models."""

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, model: Model) -> ModelMetadata:
        """
        Abstract method for fetching metadata of an AQ model.

        Parameters
        ----------
        model : Model
            The model for which metadata is to be fetched.

        Returns
        -------
        ModelMetadata
            Metadata of the AQ model.
        """
