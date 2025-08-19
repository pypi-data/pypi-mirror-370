from luna_quantum.aqm_overwrites import Model
from luna_quantum.client.interfaces.services.luna_solve_i import ILunaSolve
from luna_quantum.solve.interfaces.usecases.model_delete_usecase_i import (
    IModelDeleteUseCase,
)
from luna_quantum.util.log_utils import progress


class ModelDeleteUseCase(IModelDeleteUseCase):
    """
    Handle the deletion of models.

    This class facilitates the execution of the model delete method
    for a given Model.

    Attributes
    ----------
    client : ILunaSolve
        The client instance used for invoking the model delete method.
    """

    client: ILunaSolve

    def __init__(self, client: ILunaSolve) -> None:
        self.client = client

    @progress(total=None, desc="Deleting model...")
    def __call__(self, model: Model) -> None:
        """
        Delete the given Model from the client.

        If the Model does not have metadata, this method does nothing. It is assumed
        that the model was not stored in the client.

        Parameters
        ----------
        model : Model
            The Model instance for which the model delete method is called.

        Returns
        -------
        None
            This method does not return a value.

        """
        if model.metadata is None:
            return

        self.client.model.delete(model_id=model.metadata.id)
