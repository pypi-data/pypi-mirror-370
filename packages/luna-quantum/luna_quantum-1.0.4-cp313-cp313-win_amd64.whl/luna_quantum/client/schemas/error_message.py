from pydantic import BaseModel


class ErrorMessage(BaseModel):
    """
    Error message model.

    If an error occurs, this model is used to return error messages
    to the client. It contains the internal code and the message that describes
    the error.
    """

    internal_code: str
    message: str
