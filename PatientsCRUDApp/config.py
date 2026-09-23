# config.py
from pathlib import Path
from functools import lru_cache
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Required
    gcp_project_id: str

    # Optional / defaults
    google_application_credentials: str | None = None
    firestore_database: str = "(default)"
    firestore_emulator_host: str | None = None
    app_env: str = "development"
    log_level: str = "INFO"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()


def _apply_google_env() -> None:
    """Export credentials env vars before google-cloud SDK is imported."""
    if settings.google_application_credentials:
        path = Path(settings.google_application_credentials).resolve()
        if not path.exists():
            raise FileNotFoundError(
                f"Service account file not found: {path}\n"
                f"Check GOOGLE_APPLICATION_CREDENTIALS in .env"
            )
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(path)

    if settings.firestore_emulator_host:
        os.environ["FIRESTORE_EMULATOR_HOST"] = settings.firestore_emulator_host


_apply_google_env()