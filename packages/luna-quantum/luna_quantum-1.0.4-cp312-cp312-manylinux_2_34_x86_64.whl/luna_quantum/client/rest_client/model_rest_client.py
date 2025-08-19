from __future__ import annotations

from typing import TYPE_CHECKING, Any

from luna_quantum.aqm_overwrites.model import Model
from luna_quantum.client.interfaces.clients.model_rest_client_i import (
    IModelRestClient,
)
from luna_quantum.client.schemas.create.optimization import OptimizationUseCaseIn
from luna_quantum.client.schemas.enums.timeframe import TimeframeEnum
from luna_quantum.client.schemas.model_metadata import ModelMetadataSchema

if TYPE_CHECKING:
    from httpx import Response

    from luna_quantum.solve.use_cases import UseCase


class ModelRestClient(IModelRestClient):
    """Implementation of the model rest client."""

    @property
    def _endpoint(self) -> str:
        return "/models"

    def get_all(
        self,
        timeframe: TimeframeEnum | None = None,
        limit: int = 50,
        offset: int = 0,
        **kwargs: Any,
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
        params = {}
        if timeframe and timeframe != TimeframeEnum.all_time:  # no value == all_time
            params["timeframe"] = timeframe.value

        limit = max(limit, 1)

        params["limit"] = str(limit)
        params["offset"] = str(offset)
        response: Response = self._client.get(
            f"{self._endpoint}/metadata", params=params, **kwargs
        )
        response.raise_for_status()
        return [ModelMetadataSchema.model_validate(item) for item in response.json()]

    def get_model(self, model_id: str, **kwargs: Any) -> Model:
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
        response: Response = self._client.get(
            f"{self._endpoint}/data/{model_id}", **kwargs
        )
        response.raise_for_status()

        return Model.deserialize(response.content)

    def get_metadata_by_hash(
        self, model_hash: int, **kwargs: Any
    ) -> ModelMetadataSchema:
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
        params = {}
        params["model_hash"] = model_hash
        response: Response = self._client.get(
            f"{self._endpoint}/metadata", params=params, **kwargs
        )
        response.raise_for_status()
        models = [ModelMetadataSchema.model_validate(item) for item in response.json()]
        if len(models) != 1:
            raise ValueError(  # TODO(@Llewellyn) better error here  # noqa: E501, FIX002, TD004, TRY003
                f"Expected exactly one model with hash {model_hash}, got {len(models)}"
            )
        return models[0]

    def create(self, model: Model, **kwargs: Any) -> ModelMetadataSchema:  # noqa: ARG002
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
        response: Response = self._client.post(
            f"{self._endpoint}",
            content=model.serialize(),  # Send raw bytes directly
            headers={"Content-Type": "application/octet-stream"},
        )

        response.raise_for_status()

        return ModelMetadataSchema.model_validate(response.json())

    def get(self, model_id: str, **kwargs: Any) -> ModelMetadataSchema:
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
        response: Response = self._client.get(
            f"{self._endpoint}/metadata/{model_id}", **kwargs
        )
        response.raise_for_status()

        return ModelMetadataSchema.model_validate(response.json())

    def create_from_use_case(
        self, name: str, use_case: UseCase, **kwargs: Any
    ) -> ModelMetadataSchema:
        """
        Create a model from a use case.

        Parameters
        ----------
        name: str
            Name of the use case to be created.
        use_case: UseCase
            A use case instance that defines the optimization problem.
        **kwargs
            Parameters to pass to `httpx.request`.
        """
        optimization_in = OptimizationUseCaseIn(
            name=name, use_case=use_case, params=None
        )

        response: Response = self._client.post(
            f"{self._endpoint}/use-case",
            content=optimization_in.model_dump_json(),
            **kwargs,
        )

        response.raise_for_status()

        return ModelMetadataSchema.model_validate(response.json())

    def delete(self, model_id: str, **kwargs: Any) -> None:
        """
        Delete a model and the model metadata by its id.

        Parameters
        ----------
        model_id: str
            Id of the model to be deleted.
        **kwargs
            Parameters to pass to `httpx.request`.
        """
        response: Response = self._client.delete(
            f"{self._endpoint}/{model_id}", **kwargs
        )
        response.raise_for_status()
