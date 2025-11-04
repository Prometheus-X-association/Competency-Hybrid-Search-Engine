from configcore import Settings as CoreSettings
from pydantic import Field


class Settings(CoreSettings):
    """Configuration settings for the application."""

    search_engine_endpoint: str = Field(
        ...,
        description="URL of the Search Engine service (e.g. http://localhost:8000/entities)",
    )


settings = Settings()
