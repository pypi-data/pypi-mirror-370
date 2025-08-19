from luna_quantum.aqm_overwrites import Model
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.domain.model_metadata import ModelMetadata
from luna_quantum.solve.interfaces.usecases.model_load_by_metadata_usecase_i import (
    IModelLoadByMetadataUseCase,
)
from luna_quantum.util.log_utils import progress


class ModelLoadByMetadataUseCase(IModelLoadByMetadataUseCase):
    """
    Loads an model model using metadata.

    The purpose of this class is to load an model model from a given metadata
    object using the specified client. It retrieves the model and attaches the metadata
    to it.

    Attributes
    ----------
    client : ILunaSolve
        The client responsible for interacting with the model backend.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Retrieving model...")
    def __call__(self, model_metadata: ModelMetadata) -> Model:
        """
        Callable to retrieve and update an Model instance.

        This method interacts with the client to fetch an Model based on the
        provided ModelMetadata, updates the model's metadata, and then returns
        the updated Model instance.

        Parameters
        ----------
        model_metadata : ModelMetadata
            The metadata object containing the ID and relevant data for fetching
            the corresponding Model.

        Returns
        -------
        Model
            The fetched and updated Model instance.

        """
        aq_model: Model = self.client.model.get_model(model_id=model_metadata.id)

        return aq_model
