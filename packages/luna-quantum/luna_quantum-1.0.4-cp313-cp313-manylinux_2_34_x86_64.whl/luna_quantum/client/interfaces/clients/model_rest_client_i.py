from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from luna_quantum.client.interfaces.clients.rest_client_i import IRestClient

if TYPE_CHECKING:
    from luna_quantum.aqm_overwrites.model import Model
    from luna_quantum.client.schemas.enums.timeframe import TimeframeEnum
    from luna_quantum.client.schemas.model_metadata import ModelMetadataSchema
    from luna_quantum.solve.use_cases import UseCase


class IModelRestClient(IRestClient, ABC):
    """Interface for model rest client."""

    @abstractmethod
    def get(self, model_id: str, **kwargs: dict[str, Any]) -> ModelMetadataSchema:
        """
        Retrieve the model metadata by its id.

        Parameters
        ----------
        model_id: str
            Id of the model to be retrieved.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        ModelMetadataSchema:
            Metadata of the model.
        """

    @abstractmethod
    def get_model(self, model_id: str, **kwargs: dict[str, Any]) -> Model:
        """
        Retrieve a model by the id.

        Parameters
        ----------
        model_id: str
            Id of the model to be retrieved.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        Model:
            The model.

        """

    @abstractmethod
    def get_metadata_by_hash(self, model_hash: int) -> ModelMetadataSchema:
        """
        Retrieve metadata for a model using its hash.

        This method fetches metadata associated with a given model hash.

        Parameters
        ----------
        model_hash : int
            The hash identifier of the model.

        Returns
        -------
        ModelMetadataSchema
            Metadata information of the model.
        """

    @abstractmethod
    def get_all(
        self,
        timeframe: TimeframeEnum | None = None,
        limit: int = 50,
        offset: int = 0,
        **kwargs: dict[str, Any],
    ) -> list[ModelMetadataSchema]:
        """
        Retrieve a list of model metadata.

        Parameters
        ----------
        timeframe: Optional[TimeframeEnum]
            Only return optimizations created within a specified timeframe.
            Default None.
        limit:
            Limit the number of optimizations to be returned. Default value 50.
        offset:
            Offset the list of optimizations by this amount. Default value 0.
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        List[ModelMetadataSchema]:
            List of model metadata.
        """

    @abstractmethod
    def create(self, model: Model) -> ModelMetadataSchema:
        """
        Create a model based on the provided Model instance.

        This function saves the model and returns metadata about it.

        Parameters
        ----------
        model : Model
            Instance of the Model which should be saved.

        Returns
        -------
        ModelMetadataSchema
            Metadata of the created model containing information about its
            configuration and properties.

        """

    @abstractmethod
    def create_from_use_case(
        self, name: str, use_case: UseCase, **kwargs: Any
    ) -> ModelMetadataSchema:
        """Create a model from a use case."""

    @abstractmethod
    def delete(self, model_id: str, **kwargs: dict[str, Any]) -> None:
        """
        Delete a model and the model metadata by its id.

        Parameters
        ----------
        model_id: str
            Id of the model to be deleted.
        **kwargs
            Parameters to pass to `httpx.request`.
        """
