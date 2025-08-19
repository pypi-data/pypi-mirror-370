from luna_quantum.aqm_overwrites import Model
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.interfaces.usecases.model_load_by_id_usecase_i import (
    IModelLoadByIdUseCase,
)
from luna_quantum.util.log_utils import progress


class ModelLoadByIdUseCase(IModelLoadByIdUseCase):
    """
    Load an Model by its identifier.

    This class interacts with a client implementing ILunaSolve to fetch and load
    model models, providing their metadata and content.

    Attributes
    ----------
    client : ILunaSolve
        The client used for fetching the model models.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Retrieving model...")
    def __call__(self, model_id: str) -> Model:
        """
        Retrieve a Model object based on the given model id.

        This method fetches a model schema using the provided model identifier, converts
        it to a Model object, and validates its metadata before returning it.

        Parameters
        ----------
        model_id : str
            The unique identifier of the model to retrieve.

        Returns
        -------
        Model
            The retrieved model, with associated metadata validated and populated.
        """
        aq_model: Model = self.client.model.get_model(model_id=model_id)

        return aq_model
