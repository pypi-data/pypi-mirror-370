from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.aqm_overwrites import Model
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
    from luna_quantum.solve.domain.model_metadata import ModelMetadata


class IModelLoadByMetadataUseCase(ABC):
    """Interface for loading an AQ model using metadata."""

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, model_metadata: ModelMetadata) -> Model:
        """
        Abstract method for loading the model by the metadata.

        This method acts as an interface for running a specific AQ Model based on the
        provided metadata and returning the constructed AQ model instance.

        Parameters
        ----------
        model_metadata : ModelMetadata
            Metadata required for constructing or running the AQ Model.

        Returns
        -------
        Model
            The constructed AQ Model instance.

        """
