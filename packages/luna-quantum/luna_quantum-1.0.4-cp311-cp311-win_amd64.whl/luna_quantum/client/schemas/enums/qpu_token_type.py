from enum import Enum


class QpuTokenTypeEnum(str, Enum):
    """
    Enumeration of possible types for QPU tokens.

    This enum defines the scope or ownership category of QPU tokens.

    Attributes
    ----------
    GROUP : str
        Indicates that the QPU token is shared among a group of users.

    PERSONAL : str
        Indicates that the QPU token belongs to an individual user.
    """

    GROUP = "group"
    PERSONAL = "personal"
