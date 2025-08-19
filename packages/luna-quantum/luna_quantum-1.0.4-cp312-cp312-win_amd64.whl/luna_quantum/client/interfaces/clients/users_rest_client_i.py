from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

from luna_quantum.client.interfaces.clients.rest_client_i import IRestClient

if TYPE_CHECKING:
    from luna_quantum.client.schemas.user import User


class IUsersRestClient(IRestClient, ABC):
    """Inteface for user rest client."""

    @abstractmethod
    def get_me(self, **kwargs: dict[str, Any]) -> User:
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
