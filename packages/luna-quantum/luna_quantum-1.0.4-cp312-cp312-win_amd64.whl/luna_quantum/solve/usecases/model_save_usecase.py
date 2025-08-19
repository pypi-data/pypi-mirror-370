from typing import TYPE_CHECKING

from luna_quantum.aqm_overwrites import Model
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.domain.model_metadata import ModelMetadata
from luna_quantum.solve.interfaces.usecases.model_save_usecase_i import (
    IModelSaveUseCase,
)
from luna_quantum.util.log_utils import progress

if TYPE_CHECKING:
    from luna_quantum.client.schemas.model_metadata import ModelMetadataSchema


class ModelSaveUseCase(IModelSaveUseCase):
    """
    Represents a use case for saving an Model instance.

    Provides functionality to interface with a client implementation for
    retrieving or creating model metadata and saving model information. The
    metadata retrieved is not written to the model instance.

    Attributes
    ----------
    client : ILunaSolve
        The client used to perform operations related to saving and retrieving
        Model metadata, such as fetching metadata by hash or creating new
        metadata.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Saving model...")
    def __call__(self, model: Model) -> ModelMetadata:
        """
        Retrieve model metadata, if the model does not exist create and retrieve it.

        This function attempts to fetch the metadata of the given `Model` instance
        from the model client. If the metadata is not found, the model is saved
        with the client and the metadata is retrieved again.

        Parameters
        ----------
        model : Model
            The model instance for which metadata is being retrieved or created.

        Returns
        -------
        ModelMetadata
            The validated metadata associated with the given model instance.
        """
        metadata: ModelMetadataSchema
        try:
            metadata = self.client.model.get_metadata_by_hash(
                model_hash=model.__hash__()
            )
        except Exception:  # TODO(Llewellyn): make more specific to # noqa: FIX002
            #  Not found exception
            metadata = self.client.model.create(model=model)
        return ModelMetadata.model_validate(metadata.model_dump())
