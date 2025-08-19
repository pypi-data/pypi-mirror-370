from enum import Enum


class _RESTQpuTokenSource(str, Enum):
    """_RESTQpuTokenSource.

    This schema allow us not to change entire backend,
    but just sync SDK and everything else in terms of qpu token source.
    Currently, the difference is that
    SDK has group qpu token source
    and backend has organization qpu token source which are mapped to each other.
    """

    # token currently passed in from the API call (not stored by us)
    INLINE = "inline"
    # stored token in user account
    PERSONAL = "personal"
    # stored token in group account
    ORGANIZATION = "organization"
