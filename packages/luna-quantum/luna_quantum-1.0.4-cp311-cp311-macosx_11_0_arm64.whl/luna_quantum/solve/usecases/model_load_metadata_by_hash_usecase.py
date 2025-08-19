from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.domain.model_metadata import ModelMetadata
from luna_quantum.solve.interfaces.usecases import (
    IModelLoadMetadataByHashUseCase,
)
from luna_quantum.util.log_utils import progress


class ModelLoadMetadataByHashUseCase(IModelLoadMetadataByHashUseCase):
    """
    Load metadata for an AQ model using a hash.

    This class interacts with the client to retrieve and validate the metadata
    of an AQ model by providing its unique hash value.

    Attributes
    ----------
    client : ILunaSolve
        The client used to retrieve AQ model metadata.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Retrieving model metadata...")
    def __call__(self, model_hash: int) -> ModelMetadata:
        """
        Retrieve the metadata for a specific model using its unique hash.

        This callable retrieves the model metadata by communicating with a client
        based on the provided model hash. It validates the
        retrieved metadata against the ModelMetadata schema and returns a
        validated object.

        Parameters
        ----------
        model_hash : int
            The unique hash identifier for the model whose metadata is to be
            retrieved.

        Returns
        -------
        ModelMetadata
            A validated object containing metadata information about the model.

        """
        aq_model_schema = self.client.model.get_metadata_by_hash(model_hash=model_hash)

        return ModelMetadata.model_validate(aq_model_schema.model_dump())
