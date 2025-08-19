from enum import Enum


class SenseEnum(str, Enum):
    """Optimization Sense."""

    MAX = "max"
    MIN = "min"
