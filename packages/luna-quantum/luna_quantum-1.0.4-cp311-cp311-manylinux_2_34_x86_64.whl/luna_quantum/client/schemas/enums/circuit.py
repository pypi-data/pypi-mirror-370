from enum import Enum


class CircuitProviderEnum(str, Enum):
    """
    Enumeration of supported quantum circuit execution providers.

    Enum Values
    ----------
    IBM
        IBM quantum computing services.
    QCTRL
        Q-CTRL quantum computing services.
    AWS
        AWS quantum computing services.
    """

    IBM = "ibm"
    QCTRL = "qctrl"
    AWS = "aws"


class CircuitStatusEnum(str, Enum):
    """
    Enumeration of possible status states for a circuit job.

    Enum Values
    ----------
    IN_PROGRESS
        The circuit job is currently being executed.
    DONE
        The circuit job has completed successfully.
    FAILED
        The circuit job encountered an error during execution.
    CANCELED
        The circuit job was explicitly canceled.
    """

    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
