from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BaseAppSettings(BaseSettings):
    """Base application settings class."""

    DEBUG: bool = False
    PROJECT_NAME: str = "Task Dispatcher"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"  # Changed from default to ignore extra fields
    )


class RabbitMQSettings(BaseAppSettings):
    """RabbitMQ-specific settings."""

    APP_MQ_AGGREGATOR_URL: str = ""
    APP_MQ_CONNECTION_URL: str = ""


class CelerySettings(BaseAppSettings):
    """Celery-specific settings."""

    CELERY_BROKER_URL: str | None = None
    CELERY_RESULT_BACKEND: str | None = None


class Settings(BaseAppSettings):
    """Main settings class that combines all settings."""

    rabbitmq: RabbitMQSettings = Field(default_factory=RabbitMQSettings)
    celery: CelerySettings = Field(default_factory=CelerySettings)


@lru_cache()
def get_settings() -> Settings:
    """Create cached settings instance."""
    return Settings()
