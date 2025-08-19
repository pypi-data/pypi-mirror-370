from luna_quantum.solve.errors.solve_base_error import SolveBaseError


class TokenMissingError(SolveBaseError):
    """Exception raised, when token is missing."""

    def __init__(self) -> None:
        self.message = (
            "To complete this action, a token is required. "
            "Make sure that the token has been set."
        )
