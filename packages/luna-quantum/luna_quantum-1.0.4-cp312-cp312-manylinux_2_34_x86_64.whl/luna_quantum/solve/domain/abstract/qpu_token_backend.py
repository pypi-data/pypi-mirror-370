from abc import ABC, abstractmethod

from luna_quantum.client.schemas.qpu_token.qpu_token import TokenProvider
from luna_quantum.client.utils.qpu_token_utils import QpuTokenUtils
from luna_quantum.solve.interfaces.backend_i import IBackend


class QpuTokenBackend(IBackend, ABC):
    """Abstract base class for backend providers that require QPU tokens."""

    @abstractmethod
    def _get_token(self) -> TokenProvider | None:
        pass

    def get_qpu_tokens(self) -> TokenProvider | None:
        """
        Retrieve a QPU token.

        This method is intended to be implemented by subclasses to provide the
        mechanism for fetching the required Quantum Processing Unit (QPU) tokens, if
        they are required by the solver implementation. The tokens may either be
        sourced from a `TokenProvider` object or result in a `None` if unavailable.

        Returns
        -------
        TokenProvider | None:
            An object implementing the `TokenProvider` interface if tokens are
            available/needed, otherwise `None`.
        """
        token = self._get_token()
        if token is None:
            token = TokenProvider()

        return QpuTokenUtils.patch_qpu_tokens_from_env(token)
