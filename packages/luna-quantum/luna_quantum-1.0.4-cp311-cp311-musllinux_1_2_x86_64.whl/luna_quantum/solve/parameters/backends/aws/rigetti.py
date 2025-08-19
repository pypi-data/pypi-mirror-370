from typing import Literal

from pydantic import computed_field

from .aws_backend_base import AWSBackendBase


class Rigetti(AWSBackendBase):
    """
    Configuration parameters for Rigetti quantum backends, accessed via AWS.

    Attributes
    ----------
    device: Literal["Ankaa3"], default="Ankaa3"
        The specific Rigetti quantum device to use for computations. Currently only
        "Ankaa-3" is available - Rigetti's latest superconducting quantum processor
        featuring improved coherence times and gate fidelities.
    aws_access_key: str | QpuToken | None
        The AWS access key
    aws_secret_access_key: str | QpuToken | None
        The AWS secret access key
    aws_session_token: str | QpuToken | None
        The AWS session token
    """

    device: Literal["Ankaa3"] = "Ankaa3"

    @computed_field
    def device_provider(self) -> str:
        """Return the device provider identifier."""
        return "Rigetti"
