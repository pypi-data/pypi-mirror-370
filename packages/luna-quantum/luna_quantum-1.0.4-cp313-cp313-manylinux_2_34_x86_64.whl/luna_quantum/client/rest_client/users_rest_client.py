from __future__ import annotations

from typing import TYPE_CHECKING, Any

from luna_quantum.client.interfaces.clients import IUsersRestClient
from luna_quantum.client.schemas.user import User

if TYPE_CHECKING:
    from httpx import Response


class UsersRestClient(IUsersRestClient):
    """UsersRestClient is a class for interacting with the Luna API's users endpoint."""

    @property
    def _endpoint(self) -> str:
        return "/users"

    def get_me(self, **kwargs: Any) -> User:
        """
        Retrieve information about user.

        Parameters
        ----------
        **kwargs
            Parameters to pass to `httpx.request`.

        Returns
        -------
        User:
            User data.
        """
        response: Response = self._client.get(f"{self._endpoint}/me", **kwargs)
        response.raise_for_status()
        return User.model_validate_json(response.text)
