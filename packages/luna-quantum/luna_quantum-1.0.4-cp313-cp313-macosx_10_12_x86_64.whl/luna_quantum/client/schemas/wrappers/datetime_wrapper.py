from __future__ import annotations

from datetime import datetime
from typing import Annotated

from dateutil.parser import parse
from pydantic import BeforeValidator


def validate_datetime(date_string: str | datetime) -> datetime:
    """Validate an ISO date string and return it in the local timezone.

    Parameters
    ----------
    date_string : str
        The ISO date string

    Returns
    -------
    datetime
        The datetime in the user's local timezone

    Raises
    ------
    ValueError
        If `date_string` does not have a valid format.
    """
    dt = date_string if isinstance(date_string, datetime) else parse(date_string)
    return dt.astimezone()


PydanticDatetimeWrapper = Annotated[datetime, BeforeValidator(validate_datetime)]
