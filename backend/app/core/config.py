"""Application configuration management using Pydantic Settings.

This module defines a single Settings class that loads, validates,
and type-converts all environment variables used across the application.
"""

from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Centralized application settings loaded from environment variables.

    Attributes are automatically populated from the `.env` file at the
    project root. All values are validated and type-converted by Pydantic.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # === APP ===
    APP_NAME: str = "NexusAI"
    APP_ENV: str = "development"
    DEBUG: bool = True
    SECRET_KEY: str
    API_V1_PREFIX: str = "/api/v1"

    # === DATABASE ===
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "nexusai"
    POSTGRES_USER: str = "nexusai_user"
    POSTGRES_PASSWORD: str
    DATABASE_URL: str

    # === CHROMADB ===
    CHROMA_HOST: str = "localhost"
    CHROMA_PORT: int = 8001
    CHROMA_COLLECTION: str = "nexusai_docs"

    # === AI / LLM ===
    AI_PROVIDER: str = "ollama"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_EMBEDDING_MODEL: str = "text-embedding-3-small"

    # === OLLAMA ===
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3"

    # === JWT ===
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # === STORAGE ===
    STORAGE_TYPE: str = "local"
    LOCAL_STORAGE_PATH: str = "./uploads"
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_BUCKET_NAME: str = ""

    # === RATE LIMITING ===
    RATE_LIMIT_PER_MINUTE: int = 60

    # === CORS ===
    ALLOWED_ORIGINS: str = "http://localhost:3000"

    @field_validator("APP_ENV")
    @classmethod
    def validate_app_env(cls, value: str) -> str:
        """Ensure APP_ENV is one of the allowed environment names.

        Args:
            value: The raw APP_ENV string from the environment.

        Returns:
            The validated environment name.

        Raises:
            ValueError: If the value is not a recognized environment.
        """
        allowed = {"development", "staging", "production"}
        if value not in allowed:
            raise ValueError(f"APP_ENV must be one of {allowed}, got '{value}'")
        return value

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse the comma-separated ALLOWED_ORIGINS string into a list.

        Returns:
            A list of allowed origin URLs for CORS configuration.
        """
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]

    @property
    def is_production(self) -> bool:
        """Check whether the app is running in production mode.

        Returns:
            True if APP_ENV is 'production', False otherwise.
        """
        return self.APP_ENV == "production"


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton instance of Settings.

    Using lru_cache ensures the .env file is read and validated only
    once per process, rather than on every import or function call.

    Returns:
        The application's validated Settings instance.
    """
    return Settings()


settings = get_settings()