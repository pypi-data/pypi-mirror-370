from luna_quantum.solve.errors.solve_base_error import SolveBaseError


class ModelMetadataMissingError(SolveBaseError):
    """Exception raised for errors in the input."""

    def __init__(self) -> None:
        self.message = (
            "Model metadata is required to complete this action. "
            "Make sure that the model has been saved."
        )
