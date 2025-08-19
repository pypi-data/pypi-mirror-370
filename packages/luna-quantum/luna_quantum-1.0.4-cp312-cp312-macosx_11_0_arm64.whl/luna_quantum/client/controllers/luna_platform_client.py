from __future__ import annotations

import os
from contextlib import suppress
from enum import Enum
from http import HTTPStatus
from typing import TYPE_CHECKING, ClassVar

import httpx
from httpx import HTTPStatusError, Request, Response

from luna_quantum.client.controllers.luna_http_client import LunaHTTPClient
from luna_quantum.client.error.luna_api_key_invalid_error import LunaApiKeyInvalidError
from luna_quantum.client.error.luna_api_key_missing_error import LunaApiKeyMissingError
from luna_quantum.client.error.utils.http_error_utils import HttpErrorUtils
from luna_quantum.client.interfaces.services.service_i import IService
from luna_quantum.client.rest_client.users_rest_client import UsersRestClient

if TYPE_CHECKING:
    from collections.abc import Generator


class LunaPrefixEnum(str, Enum):
    """Enumeration of Luna services."""

    LUNA_SOLVE = "luna-solve"
    LUNA_Q = "luna-q"


def check_httpx_exceptions(response: Response) -> None:
    """
    Check if response contains errors from the server.

    This function examines the HTTP response and raises appropriate SDK exceptions
    if error conditions are detected.

    Parameters
    ----------
    response: Response
        The HTTP response object to be examined for error conditions.
    """
    HttpErrorUtils.check_for_error(response)


class APIKeyAuth(httpx.Auth):
    """API key authentication method for luna platform."""

    def __init__(self, token: str) -> None:
        self.token = token

    def auth_flow(self, request: Request) -> Generator[Request, Response]:
        """
        Authenticate a request to Luna platform.

        Parameters
        ----------
        request: Request
            Request that needs to be authenticated.
        """
        request.headers["Luna-API-Key"] = self.token

        dev_header_value = os.getenv("LUNA_DEV_EXTRA_HEADER_VALUE", None)
        dev_header_name = os.getenv("LUNA_DEV_EXTRA_HEADER_NAME", None)
        if dev_header_name and dev_header_value:
            request.headers[dev_header_name] = dev_header_value
        yield request


class LunaPlatformClient(IService):
    """Luna platform REST client."""

    _base_url: str = ""

    _httpx_client: httpx.Client
    _api_key: ClassVar[str | None] = None

    @property
    def client(self) -> httpx.Client:
        """
        Return httpx client.

        Returns
        -------
        httpx.Client
        """
        return self._httpx_client

    def __init__(
        self,
        api: LunaPrefixEnum,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = 240.0,
    ) -> None:
        """
        LunaPlatformClient is a main entrypoint of the SDK.

        All the operations with entities should be processed using an instance of
        LunaPlatformClient.

        Parameters
        ----------
        api: LunaPrefixEnum
            Current API with which luna client is working. Can be luna-solve or luna-q.
        api_key: Optional[str]
            Api key to be used to authorize. Default none.
            If its none then the key set by the `authorize` method will be used.
        base_url:
            Base API URL.
            If you want to use API not on your local PC then change it.
            You can do that by setting the environment variable LUNA_BASE_URL.
            Default value https://api.aqarios.com.
        timeout:
            Default timeout in seconds for the requests via the LunaQ client. `None`
            means that the SDK uses no timeouts. Note that either way the Luna platform
            itself will time out after 240 seconds.
            Default: 240.0
        """
        if base_url is None:
            base_url = os.getenv("LUNA_BASE_URL", "https://api.aqarios.com")
        if os.getenv("LUNA_DISABLE_SUFFIX", "false").lower() == "true":
            self._base_url = f"{base_url}/api/v1"
        else:
            self._base_url = f"{base_url}/{api.value}/api/v1"
        if api_key:
            auth_key = api_key
        elif self.__class__._api_key:  # noqa: SLF001 Use here self.__class__ so that LunaSolve and LunaQ can have different api keys set
            auth_key = self.__class__._api_key  # noqa: SLF001 Use here self.__class__ so that LunaSolve and LunaQ can have different api keys set
        elif key := os.getenv("LUNA_API_KEY", None):
            auth_key = key
        else:
            raise LunaApiKeyMissingError

        self._httpx_client = LunaHTTPClient(
            auth=APIKeyAuth(auth_key),
            base_url=self._base_url,
            follow_redirects=True,
            timeout=timeout,
            event_hooks={"response": [check_httpx_exceptions]},
        )

        self._authenticate()

    def __del__(self) -> None:  # noqa: D105
        if hasattr(self, "_httpx_client"):
            with suppress(Exception):
                self._httpx_client.close()

    def _authenticate(self) -> None:
        try:
            UsersRestClient(service=self).get_me()
        except HTTPStatusError as exception:
            if exception.response.status_code == HTTPStatus.UNAUTHORIZED:
                raise LunaApiKeyInvalidError from exception
            raise
