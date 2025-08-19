from luna_quantum.client.error.luna_error import LunaError


class LunaApiKeyMissingError(LunaError):
    """Raised when the Luna API key is missing."""

    def __init__(self) -> None:
        super().__init__(
            "Luna API key is missing. Please set the LUNA_API_KEY environment variable."
        )
