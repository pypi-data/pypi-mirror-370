from luna_quantum.client.error.luna_error import LunaError


class LunaApiKeyInvalidError(LunaError):
    """Raised when the Luna API key is invalid."""

    def __init__(self) -> None:
        super().__init__(
            "Luna API key is invalid. Please provide a valid Luna API key."
        )
