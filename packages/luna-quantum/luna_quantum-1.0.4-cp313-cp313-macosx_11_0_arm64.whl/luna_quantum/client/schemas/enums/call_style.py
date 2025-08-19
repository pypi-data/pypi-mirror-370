from enum import Enum


class CallStyle(str, Enum):
    """
    Enumeration of all supported call styles.

    This enumeration is used to prevent FBT001.
    https://docs.astral.sh/ruff/rules/boolean-type-hint-positional-argument/
    """

    ACTIVE_WAITING = "active_waiting"
    SINGLE_FETCH = "single_fetch"
