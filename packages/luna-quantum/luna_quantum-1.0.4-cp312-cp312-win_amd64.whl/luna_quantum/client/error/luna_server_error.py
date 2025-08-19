from luna_quantum.client.error.luna_error import LunaError
from luna_quantum.client.schemas.error_message import ErrorMessage


class LunaServerError(LunaError):
    """Luna HTTP server error."""

    http_status_code: int
    error_message: ErrorMessage

    def __init__(self, http_status_code: int, error_message: ErrorMessage) -> None:
        self.http_status_code = http_status_code
        self.error_message = error_message
        super().__init__(error_message.message)

    def __str__(self) -> str:  # noqa: D105
        return (
            f"The Luna-Server reported the error '{self.error_message.internal_code}' "
            f"with the message:\n {self.error_message.message}"
        )
