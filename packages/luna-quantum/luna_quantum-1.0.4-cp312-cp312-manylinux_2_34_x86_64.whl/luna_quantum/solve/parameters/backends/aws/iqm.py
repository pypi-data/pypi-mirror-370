from typing import Literal

from pydantic import computed_field

from .aws_backend_base import AWSBackendBase


class IQM(AWSBackendBase):
    """
    Configuration parameters for IQM quantum backends, accessed via AWS.

    Attributes
    ----------
    device: Literal["Garnet"], default="Garnet"
        The specific IQM quantum device to use for computations. Currently only
        "Garnet" is available - IQM's superconducting quantum processor with
        native two-qubit gates and optimized for near-term algorithms.
    aws_access_key: str | QpuToken | None
        The AWS access key
    aws_secret_access_key: str | QpuToken | None
        The AWS secret access key
    aws_session_token: str | QpuToken | None
        The AWS session token
    """

    device: Literal["Garnet"] = "Garnet"

    @computed_field
    def device_provider(self) -> str:
        """Return the device provider identifier."""
        return "IQM"
