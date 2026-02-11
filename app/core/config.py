from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pydantic import field_validator, ValidationInfo


class Settings(BaseSettings):
    PROJECT_NAME: str = "Async Cookbook API"
    ENV: str = "dev"

    API_SECRET_KEY: Optional[str] = None

    # Database
    DATABASE_URL: Optional[str] = None
    DATABASE_URL_DOCKER: Optional[str] = None

    # Redis
    REDIS_URL: Optional[str] = None

    # Sentry
    SENTRY_DSN: Optional[str] = None

    # Email (Reused from your old homework)
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator(
        "DATABASE_URL", "REDIS_URL", "SMTP_USER", "SMTP_PASSWORD", "SMTP_HOST"
    )
    @classmethod
    def check_required_fields(cls, v: Optional[str], info: ValidationInfo) -> str:
        if v is None:
            raise ValueError(f"{info.field_name} is missing from .env!")
        return v


settings = Settings()
