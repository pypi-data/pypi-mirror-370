from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
    from luna_quantum.solve.domain.model_metadata import ModelMetadata


class IModelLoadMetadataByHashUseCase(ABC):
    """Interface for loading model metadata by hash."""

    @abstractmethod
    def __init__(self, client: ILunaSolve) -> None:
        pass

    @abstractmethod
    def __call__(self, model_hash: int) -> ModelMetadata:
        """
        Abstract base class for callable objects that provide Model metadata.

        This class defines a contract for objects that, when called, return
        metadata associated with a particular Model specified by a unique
        hash value.

        Parameters
        ----------
        model_hash : int
            A hash value uniquely identifying the Model for which metadata
            is requested.

        Returns
        -------
        ModelMetadata
            Metadata associated with the specified Model.

        """
