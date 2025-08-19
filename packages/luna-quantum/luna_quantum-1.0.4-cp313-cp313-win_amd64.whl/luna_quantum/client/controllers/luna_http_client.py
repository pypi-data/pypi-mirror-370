from __future__ import annotations

from importlib.metadata import version
from typing import Any

import httpx
from httpx import Client, Response

from luna_quantum.client.error.timeout_error import LunaTimeoutError
from luna_quantum.client.error.utils.http_error_utils import HttpErrorUtils


class LunaHTTPClient(Client):
    """
    Luna HTTP client.

    Mainly used to set custom headers.
    """

    _version: str = version("luna-quantum")

    _user_agent: str = f"LunaSDK/{_version}"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        self.headers["User-Agent"] = self._user_agent

    def request(self, *args: Any, **kwargs: Any) -> Response:
        """Send request to Luna platform."""
        try:
            response: Response = super().request(*args, **kwargs)
        except httpx.TimeoutException:
            # Handle all possible in httpx timeout exceptions
            raise LunaTimeoutError from None
        HttpErrorUtils.check_for_error(response)
        return response
