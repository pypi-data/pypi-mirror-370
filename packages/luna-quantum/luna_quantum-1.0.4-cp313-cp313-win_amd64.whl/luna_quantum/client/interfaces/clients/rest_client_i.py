from abc import ABC, abstractmethod

from httpx import Client

from luna_quantum.client.interfaces.services.service_i import IService


class IRestClient(ABC):
    """Inteface for rest client."""

    _lc_client: IService
    _client: Client

    def __init__(self, service: IService) -> None:
        self._lc_client = service
        self._client = service.client

    @property
    @abstractmethod
    def _endpoint(self) -> str:
        raise NotImplementedError
