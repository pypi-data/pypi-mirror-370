from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field

from luna_quantum.client.schemas.enums.qpu_token_type import (
    QpuTokenTypeEnum,
)


class QpuTokenSource(str, Enum):
    """
    Enumeration of possible sources for QPU tokens.

    This enum defines the different strategies for providing or retrieving
    QPU tokens.
    """

    # token currently passed in from the API call
    INLINE = "inline"
    # stored token in user account
    PERSONAL = "personal"
    # stored token in group account
    GROUP = "group"


class QpuToken(BaseModel):
    """
    Schema for QPU token.

    Attributes
    ----------
    source: QpuTokenSource
        Specifies the source location of the QPU token, determining how the
        token is retrieved.
    name: str | None
        The identifier name of the stored QPU token. Required when
        source is QpuTokenSource.PERSONAL or QpuTokenSource.GROUP.
    token: str | None
        The actual QPU token value to be used for authentication.
        Required when source is QpuTokenSource.INLINE.
    """

    source: QpuTokenSource
    # A unique name for a stored token
    name: str | None = None
    # This could be a QPU token, an API key or any token key for a QPU provider.
    # If the token is not passed from this API call, one stored in the user's
    # account will be used.
    token: str | None = None


class PersonalQpuToken(QpuToken):
    """
    Schema for stored personal qpu token.

    Attributes
    ----------
    name: str
        Name of qpu token.
    source: QpuTokenSource
        Source of the qpu token.
        In this case should be always set to QpuTokenSource.PERSONAL
    """

    name: str
    source: QpuTokenSource = Field(
        init=False, default=QpuTokenSource.PERSONAL, frozen=True
    )


class GroupQpuToken(QpuToken):
    """
    Schema for stored group qpu token.

    Attributes
    ----------
    name: str
        Name of qpu token.
    source: QpuTokenSource
        Source of the qpu token.
        In this case should be always set to QpuTokenSource.GROUP
    """

    name: str
    source: QpuTokenSource = Field(
        init=False, default=QpuTokenSource.GROUP, frozen=True
    )


class TokenProvider(BaseModel):
    """
    Schema for QPU tokens.

    Attributes
    ----------
    dwave: QpuToken | None
        Authentication token for D-Wave quantum computing services.
        None if no D-Wave token is provided.

    ibm: QpuToken | None
        Authentication token for IBM Quantum services.
        None if no IBM token is provided.

    fujitsu: QpuToken | None
        Authentication token for Fujitsu quantum computing services.
        None if no Fujitsu token is provided.

    qctrl: QpuToken | None
        Authentication token for Q-CTRL quantum computing services.
        None if no Q-CTRL token is provided.

    aws_access_key: QpuToken
        The AWS access key ID token used to identify the AWS account.

    aws_secret_access_key: _RestQpuToken
        The AWS secret access key token used to verify the identity.

    aws_session_token: _RestQpuToken
        The AWS session token.
    """

    dwave: QpuToken | None = None
    ibm: QpuToken | None = None
    fujitsu: QpuToken | None = None
    qctrl: QpuToken | None = None
    aws_access_key: QpuToken | None = None
    aws_secret_access_key: QpuToken | None = None
    aws_session_token: QpuToken | None = None

    model_config = ConfigDict(extra="forbid")


class QpuTokenOut(BaseModel):
    """
    pydantic model for qpu token out.

    it contains the data received from the api call.

    Attributes
    ----------
    name: optional[str]
        name of the qpu token.
    provider: str
        name of provider.

    """

    name: str
    provider: str
    token_type: QpuTokenTypeEnum

    model_config = ConfigDict(extra="forbid", from_attributes=True)
