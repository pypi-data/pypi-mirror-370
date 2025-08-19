from datetime import datetime
from typing import Any

from pydantic import BaseModel

from luna_quantum.client.schemas.enums.model_format import ModelFormat
from luna_quantum.client.schemas.enums.status import StatusEnum


class SolveJobSchema(BaseModel):
    """
    Solve job schema.

    Attributes
    ----------
    id: str
        The ID of the solve job.
    status: StatusEnum
        The current status of the solve job.
    status_timeline: dict[StatusEnum, datetime]
        The history of status changes for the solve job.
    used_format: ModelFormat | None
        The format that is used for solving. None if not applicable.
    error_message: str | None
        The error message if the solve job failed.
    provider: str
        The name of the provider where the solve job is scheduled.
    solver_job_info: str | None
        Additional information about the solve job. None if not available.
    is_cancelable: bool
        Indicates if the solve job can be cancelled.
    is_cancellation_requested: bool
        Indicates if cancellation of the solve job has been requested.
    """

    id: str
    status: StatusEnum
    status_timeline: dict[StatusEnum, datetime]
    used_format: ModelFormat | None = None

    error_message: str | None
    provider: str

    # TODO(Lev): Consider renaming? # noqa: FIX002
    solver_job_info: str | None = None

    is_cancelable: bool
    is_cancellation_requested: bool

    metadata: dict[str, Any] | None = None
