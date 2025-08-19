from datetime import datetime

from pydantic import BaseModel


class QpuTokenTimeQuotaOut(BaseModel):
    """
    Pydantic model for QPU token time quota OUT.

    It contains the data received from the API call.

    Attributes
    ----------
    quota: int
        The total amount of quota available on a qpu token.
    start: datetime
        Effective start date of the time quota policy.
    end: datetime
        Effective end date of the time quota policy.
    quota_used: int
        How much quota has already been used from
        the totally available amount of quota.
    """

    quota: int
    start: datetime
    end: datetime
    quota_used: int
