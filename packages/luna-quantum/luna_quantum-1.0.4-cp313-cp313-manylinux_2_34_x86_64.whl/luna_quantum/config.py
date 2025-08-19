from pydantic_settings import BaseSettings


class Config(BaseSettings):
    """Class for all config values."""

    LUNA_LOG_DEFAULT_LEVEL: str = "INFO"
    LUNA_LOG_DISABLE_SPINNER: bool = False


config = Config()
