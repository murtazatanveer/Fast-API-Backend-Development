from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL 

CONFIG_DIR = Path(__file__).resolve().parent
ENV_FILE = CONFIG_DIR / ".env"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    db_user: str
    db_pass: str
    db_host: str
    db_port: int
    db_name: str

    db_echo: bool

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_issuer: str = "jwt-auth-system"
    jwt_audience: str = "jwt-auth-client"
    access_token_expire_minutes: int = 15

    refresh_sliding_days: int = 30
    refresh_absolute_days: int = 90
    refresh_cookie_name: str = "refresh_token"
    refresh_cookie_secure: bool = True
    refresh_cookie_samesite: str = "lax"

    resend_api_key: str
    otp_from_email: str
    otp_expire_minutes: int = 2
    otp_max_attempts: int = 3

    @property
    def database_url(self) -> URL:
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.db_user,
            password=self.db_pass,
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            query={"ssl": "require"}
        )

@lru_cache
def getSettings() -> Settings:
    return Settings()

settings = getSettings()