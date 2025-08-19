from enum import Enum


class StatusEnum(str, Enum):
    """
    Enumeration of possible status states for a solve job.

    This enum defines the standard lifecycle states of a solve job.

    Enum Values
    -----------
    REQUESTED
        The job has been requested but not yet initialized by the system.
        This is the initial state when a job is submitted.

    CREATED
        The job has been created and initialized in the system, but execution
        has not yet begun.

    IN_PROGRESS
        The job is currently being executed. Processing has started but
        is not yet complete.

    DONE
        The job has completed successfully with a valid result.

    FAILED
        The solve job has terminated abnormally or
        encountered an error during execution.

    CANCELED
        The job was explicitly canceled by a user before completion.
    """

    REQUESTED = "REQUESTED"
    CREATED = "CREATED"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"
    FAILED = "FAILED"
    CANCELED = "CANCELED"
