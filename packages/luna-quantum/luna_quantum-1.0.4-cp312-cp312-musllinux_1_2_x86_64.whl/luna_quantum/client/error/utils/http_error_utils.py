from __future__ import annotations

from http import HTTPStatus

import httpx
from httpx import RequestError, Response

from luna_quantum.client.error.luna_server_error import LunaServerError
from luna_quantum.client.schemas.error_message import ErrorMessage
from luna_quantum.util.log_utils import Logging

logger = Logging.get_logger(__name__)


class HttpErrorUtils:
    """Class for handling Luna HTTP errors."""

    @staticmethod
    def __sdk_custom_request_errors(
        response: Response,
    ) -> LunaServerError | None:
        """
        Check if the response needs a custom error message from the SDK.

        This is the place to add other custom error messages.
        It's helpful then the default http error messages are not enough for the user.

        Parameters
        ----------
        response:
            Response object from the request

        Returns
        -------
        Optional[LunaServerError]
            If the response needs a custom error message, return the exception.
            Otherwise, return None.
        """
        exception: LunaServerError | None = None

        def create_error_message(internal_code: str, message: str) -> LunaServerError:
            return LunaServerError(
                response.status_code,
                ErrorMessage(
                    internal_code=f"SDK-{internal_code}",
                    message=message,
                ),
            )

        if response.status_code == HTTPStatus.BAD_GATEWAY:
            # Catch error when upload was too long
            exception = create_error_message(
                "LUNA_GATEWAY_TIMEOUT",
                "The Luna server did not respond within time,"
                " leading to a timeout. Try reducing the size of the model.",
            )

        elif response.status_code == HTTPStatus.FORBIDDEN:
            exception = create_error_message(
                "FORBIDDEN",
                response.text,
            )

        return exception

    @staticmethod
    def check_for_error(response: Response) -> None:
        """
        Check if an error occurred and rais the error if so.

        Parameters
        ----------
        response: Response
            Response object from the request

        Raises
        ------
        LunaServerException
            If an error occurred with the request.
            The error message is in the exception.
        RequestError
            If an error occurred with the request outside the http status codes
             4xx and 5xx.
        """
        try:
            response.read()
            response.raise_for_status()
        except httpx.HTTPStatusError:
            exception: LunaServerError | None

            try:
                error_msg: ErrorMessage = ErrorMessage.model_validate_json(
                    response.text
                )
                # Convert the error message to the correct exception
                exception = LunaServerError(response.status_code, error_msg)

            except ValueError:
                # The server can generate errors that are in a different format, and we
                # have less to no control how they look like.
                # In this case, we will try to create a custom error messages.
                exception = HttpErrorUtils.__sdk_custom_request_errors(response)

            if exception:
                logger.exception(exception, exc_info=False)
                raise exception from None
            logger.error(exception, exc_info=True)
            raise

        except RequestError as e:
            logger.error(e, exc_info=True)
            raise
