"""
Centralized application configuration.

All environment-dependent values (DB connection, JWT secrets, etc.) are
read from environment variables / .env here, so the rest of the codebase
never touches os.environ directly.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str

    # JWT auth
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 90

    # Misc
    ENVIRONMENT: str = "development"
    PROJECT_NAME: str = "CircleUp"
    API_V1_PREFIX: str = "/api/v1"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()