from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from luna_quantum.client.schemas.qpu_token.qpu_token import (
    QpuToken,
    QpuTokenSource,
    TokenProvider,
)
from luna_quantum.client.schemas.qpu_token.qpu_token_source import _RESTQpuTokenSource


class _RestQpuToken(BaseModel):
    source: _RESTQpuTokenSource
    # A unique name for a stored token
    name: str | None = None
    # This could be a QPU token, an API key or any token key for a QPU provider.
    # If the token is not passed from this API call, one stored in the user's
    # account will be used.
    token: str | None = None

    @classmethod
    def from_qpu_token(cls, qpu_token: QpuToken | None) -> _RestQpuToken | None:
        if qpu_token is None:
            return None
        # Organizational tokens were renamed to group in #1851
        # For smoother transition we only change naming in the SDK,
        # and therefore we need a mapping between Group and Organization here.
        # However, in backend for now QPU tokens still has source organization
        # TODO: Remove it when backend I/O schema is changed # noqa: FIX002, TD002
        if qpu_token.source == QpuTokenSource.GROUP:
            return cls(
                source=_RESTQpuTokenSource.ORGANIZATION,
                name=qpu_token.name,
                token=qpu_token.token,
            )
        return cls.model_validate(qpu_token, from_attributes=True)


class AWSQpuTokens(BaseModel):
    """
    Container for AWS authentication tokens.

    Attributes
    ----------
    aws_access_key: _RestQpuToken
        The AWS access key ID token used to identify the AWS account.

    aws_secret_access_key: _RestQpuToken
        The AWS secret access key token used to verify the identity.

    aws_session_token: _RestQpuToken
        The AWS secret access key token used to verify the identity.
    """

    aws_access_key: _RestQpuToken
    aws_secret_access_key: _RestQpuToken
    aws_session_token: _RestQpuToken


class RestAPITokenProvider(BaseModel):
    """
    Internal schema for QPU tokens.

    Attributes
    ----------
    dwave: _RestQpuToken | None
        Authentication token for D-Wave quantum computing services.
        None if no D-Wave token is provided.

    ibm: _RestQpuToken | None
        Authentication token for IBM Quantum services.
        None if no IBM token is provided.

    fujitsu: _RestQpuToken | None
        Authentication token for Fujitsu quantum computing services.
        None if no Fujitsu token is provided.

    qctrl: _RestQpuToken | None
        Authentication token for Q-CTRL quantum computing services.
        None if no Q-CTRL token is provided.

    aws: AWSQpuTokens | None
        Authentication tokens for AWS quantum computing services.
        Uses a specialized structure for AWS authentication.
        None if no AWS tokens are provided.
    """

    dwave: _RestQpuToken | None = None
    ibm: _RestQpuToken | None = None
    fujitsu: _RestQpuToken | None = None
    qctrl: _RestQpuToken | None = None
    aws: AWSQpuTokens | None = None

    model_config = ConfigDict(extra="forbid")

    @classmethod
    def from_sdk_token_provider(
        cls, token_provider: TokenProvider
    ) -> RestAPITokenProvider:
        """
        Create RestAPITokenProvider from TokenProvider.

        Parameters
        ----------
        token_provider: TokenProvider
            TokenProvider datastructure containing QPU tokens.
        """
        aws: AWSQpuTokens | None = None
        if (
            token_provider.aws_access_key is not None
            or token_provider.aws_secret_access_key is not None
            or token_provider.aws_session_token is not None
        ):
            aws = AWSQpuTokens(
                aws_access_key=_RestQpuToken.from_qpu_token(  # type: ignore[arg-type]
                    token_provider.aws_access_key
                ),
                aws_secret_access_key=_RestQpuToken.from_qpu_token(  # type: ignore[arg-type]
                    token_provider.aws_secret_access_key
                ),
                aws_session_token=_RestQpuToken.from_qpu_token(  # type: ignore[arg-type]
                    token_provider.aws_session_token
                ),
            )
        return cls(
            dwave=_RestQpuToken.from_qpu_token(token_provider.dwave),
            ibm=_RestQpuToken.from_qpu_token(token_provider.ibm),
            fujitsu=_RestQpuToken.from_qpu_token(token_provider.fujitsu),
            qctrl=_RestQpuToken.from_qpu_token(token_provider.qctrl),
            aws=aws,
        )
