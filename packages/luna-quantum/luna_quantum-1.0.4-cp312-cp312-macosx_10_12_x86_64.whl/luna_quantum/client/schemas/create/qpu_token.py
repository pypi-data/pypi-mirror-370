from pydantic import BaseModel, ConfigDict


class QpuTokenIn(BaseModel):
    """
    Pydantic model for creation QPU token.

    Attributes
    ----------
    name: str
        Name of the QPU token
    provider: ProviderEnum
        Name of provider
    token: str
        Token
    """

    name: str
    provider: str
    token: str

    model_config = ConfigDict(extra="forbid")
