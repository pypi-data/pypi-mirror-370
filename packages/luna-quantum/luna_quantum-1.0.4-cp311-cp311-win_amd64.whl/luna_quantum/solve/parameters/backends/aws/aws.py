from typing import Literal

from pydantic import computed_field

from .aws_backend_base import AWSBackendBase


class AWS(AWSBackendBase):
    """
    Configuration parameters for AWS simulator backends.

    Attributes
    ----------
    device: Literal["SV1", "DM1", "TN1"], default="SV1"
        The specific AWS simulator to use for computations. Options are:

        - "SV1": State vector simulator for smaller quantum circuits
        - "DM1": Density matrix simulator for noisy quantum circuits
        - "TN1": Tensor network simulator for larger quantum circuits

        See the [AWS Braket
        docs](https://docs.aws.amazon.com/braket/latest/developerguide/choose-a-simulator.html)
    aws_access_key: str | QpuToken | None
        The AWS access key
    aws_secret_access_key: str | QpuToken | None
        The AWS secret access key
    aws_session_token: str | QpuToken | None
        The AWS session token
    """

    @computed_field
    def device_provider(self) -> str:
        """Return the device provider identifier."""
        return "Amazon"

    device: Literal["SV1", "DM1", "TN1"] = "SV1"
