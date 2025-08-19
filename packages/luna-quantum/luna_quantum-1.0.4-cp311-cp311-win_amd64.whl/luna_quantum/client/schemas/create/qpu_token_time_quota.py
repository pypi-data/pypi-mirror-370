from __future__ import annotations

from pydantic import BaseModel

from luna_quantum.client.schemas.wrappers import PydanticDatetimeWrapper


class QpuTokenTimeQuotaIn(BaseModel):
    """
    Pydantic model for creating a time quota on a qpu token.

    Attributes
    ----------
    quota: int
        The amount of quota.
    start: datetime | None
        Effective start date of the time quota policy.
        If None, policy will be in effect immediately.
    end: datetime | None
        Effective end date of the time quota policy.
        If None, policy will be in effect until 365 days after the start date.
    """

    quota: int
    start: PydanticDatetimeWrapper | None
    end: PydanticDatetimeWrapper | None
