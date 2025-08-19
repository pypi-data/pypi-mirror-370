from luna_quantum.client.error.luna_error import LunaError


class LunaTimeoutError(LunaError):
    """Luna timeout error."""

    def __init__(self) -> None:
        super().__init__(
            "Luna Timeout. The request took too long to complete."
            " Please increase timeout value or try again later."
            " If the problem persists, please contact our support team."
        )
