from abc import ABC, abstractmethod

from pydantic import BaseModel, ConfigDict


class IBackend(BaseModel, ABC):
    """
    Base interface for backend providers.

    Defines an abstract interface for backend providers. This is used as a
    base class for implementing and configuring specific backend providers.
    """

    @property
    @abstractmethod
    def provider(self) -> str:
        """
        Retrieve the name of the provider.

        Returns
        -------
        str
            The name of the provider.
        """

    model_config = ConfigDict(
        extra="forbid",
    )
