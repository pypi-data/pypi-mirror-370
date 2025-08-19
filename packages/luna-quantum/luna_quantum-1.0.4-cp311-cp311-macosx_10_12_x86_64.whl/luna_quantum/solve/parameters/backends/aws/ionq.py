from typing import Literal

from pydantic import computed_field

from .aws_backend_base import AWSBackendBase


class IonQ(AWSBackendBase):
    """
    Configuration parameters for IonQ quantum backends, accessed via AWS.

    Attributes
    ----------
    device: Literal["Aria1", "Aria2", "Forte1", "ForteEnterprise1"], \
        default="Aria1"
        The specific IonQ quantum device to use for computations. Options are:

        - "Aria1": IonQ's flagship trapped-ion quantum computer
        - "Aria2": Next-generation IonQ system with improved connectivity
        - "Forte1": IonQ's enterprise-grade quantum system
        - "ForteEnterprise1": Enhanced enterprise version with dedicated access

        Different devices have varying characteristics such as qubit count,
        connectivity, and error rates.
    aws_access_key: str | QpuToken | None
        The AWS access key
    aws_secret_access_key: str | QpuToken | None
        The AWS secret access key
    aws_session_token: str | QpuToken | None
        The AWS session token
    """

    device: Literal[
        "Aria1",
        "Aria2",
        "Forte1",
        "ForteEnterprise1",
    ] = "Aria1"

    @computed_field
    def device_provider(self) -> str:
        """Return the device provider identifier."""
        return "IonQ"
