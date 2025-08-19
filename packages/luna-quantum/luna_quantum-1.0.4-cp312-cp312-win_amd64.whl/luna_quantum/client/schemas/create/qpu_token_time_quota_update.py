from pydantic import BaseModel, ConfigDict

from luna_quantum.client.schemas.wrappers.datetime_wrapper import (
    PydanticDatetimeWrapper,
)


class QpuTokenTimeQuotaUpdate(BaseModel):
    """Data structure to update the time quota of a qpu token."""

    quota: int | None = None
    start: PydanticDatetimeWrapper | None = None
    end: PydanticDatetimeWrapper | None = None

    model_config = ConfigDict(extra="forbid")
