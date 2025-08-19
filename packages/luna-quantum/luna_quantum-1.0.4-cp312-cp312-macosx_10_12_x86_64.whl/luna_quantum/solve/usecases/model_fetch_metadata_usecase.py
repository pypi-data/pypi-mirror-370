from luna_quantum.aqm_overwrites import Model
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.domain.model_metadata import ModelMetadata
from luna_quantum.solve.interfaces.usecases.model_fetch_metadata_usecase_i import (
    IModelFetchMetadataUseCase,
)
from luna_quantum.util.log_utils import progress


class ModelFetchMetadataUseCase(IModelFetchMetadataUseCase):
    """Use case for fetching metadata of an AQ model.

    The `ModelFetchMetadataUseCase` works with a given client interface to
    retrieve metadata for a specified AQ model.

    Attributes
    ----------
    client : ILunaSolve
        Client used to fetch the metadata for an AQ model.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Fetching model...")
    def __call__(self, model: Model) -> ModelMetadata:
        """
        Fetch the metadata of the given Model.

        Load the metadata associated with the given Model instance from the client.
        The metadata is validated before returning it. The metadata is not written to
        the Model instance.

        Parameters
        ----------
        model : Model
            The Model instance to be associated with metadata.

        Returns
        -------
        ModelMetadata
            The metadata associated with the provided Model.
        """
        metadata_schema = self.client.model.get_metadata_by_hash(
            model_hash=model.__hash__()
        )

        return ModelMetadata.model_validate(metadata_schema.model_dump())
