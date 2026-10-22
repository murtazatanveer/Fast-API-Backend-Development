# Configuration/config.py
from pathlib import Path
from functools import lru_cache
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

CONFIG_DIR = Path(__file__).resolve().parent
ENV_FILE = CONFIG_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),  # <-- Uses the absolute path!
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    gcp_project_id: str
    google_application_credentials: str 
    firestore_database: str 
    app_env: str 
    log_level: str 

    jwt_secret_key: str
    jwt_algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_days: int


@lru_cache
def get_settings() -> Settings:
    return Settings()

settings = get_settings()


def _apply_google_env() -> None:
    if settings.google_application_credentials:
        path = Path(settings.google_application_credentials)
        
        if not path.is_absolute():
            path = CONFIG_DIR / path
            
        path = path.resolve()
        
        if not path.exists():
            raise FileNotFoundError(f"Credentials file not found: {path}")
            
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(path)

_apply_google_env()