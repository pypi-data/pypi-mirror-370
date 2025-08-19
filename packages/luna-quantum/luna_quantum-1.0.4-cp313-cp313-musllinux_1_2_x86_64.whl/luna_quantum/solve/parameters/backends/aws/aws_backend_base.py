from pydantic import Field

from luna_quantum.client.schemas.qpu_token.qpu_token import (
    QpuToken,
    QpuTokenSource,
    TokenProvider,
)
from luna_quantum.solve.domain.abstract.qpu_token_backend import QpuTokenBackend


class AWSBackendBase(QpuTokenBackend):
    """AWS Backend Mixin.

    Attributes
    ----------
    aws_access_key: str | QpuToken | None
        The AWS access key
    aws_secret_access_key: str | QpuToken | None
        The AWS secret access key
    aws_session_token: str | QpuToken | None
        The AWS session token
    """

    aws_access_key: str | QpuToken | None = Field(
        repr=False, exclude=True, default=None
    )
    aws_secret_access_key: str | QpuToken | None = Field(
        repr=False, exclude=True, default=None
    )
    aws_session_token: str | QpuToken | None = Field(
        repr=False, exclude=True, default=None
    )

    @property
    def provider(self) -> str:
        """
        Retrieve the name of the provider.

        Returns
        -------
        str
            The name of the provider.
        """
        return "aws"

    def _get_token(self) -> TokenProvider | None:
        if self.aws_access_key is None and self.aws_secret_access_key is None:
            return None

        token_provider = TokenProvider()
        if isinstance(self.aws_access_key, QpuToken):
            token_provider.aws_access_key = self.aws_access_key
        elif isinstance(self.aws_access_key, str):
            token_provider.aws_access_key = QpuToken(
                source=QpuTokenSource.INLINE,
                token=self.aws_access_key,
            )

        if isinstance(self.aws_secret_access_key, QpuToken):
            token_provider.aws_secret_access_key = self.aws_secret_access_key
        elif isinstance(self.aws_secret_access_key, str):
            token_provider.aws_secret_access_key = QpuToken(
                source=QpuTokenSource.INLINE,
                token=self.aws_secret_access_key,
            )

        if isinstance(self.aws_session_token, QpuToken):
            token_provider.aws_session_token = self.aws_session_token
        elif isinstance(self.aws_session_token, str):
            token_provider.aws_session_token = QpuToken(
                source=QpuTokenSource.INLINE,
                token=self.aws_session_token,
            )
        return token_provider
