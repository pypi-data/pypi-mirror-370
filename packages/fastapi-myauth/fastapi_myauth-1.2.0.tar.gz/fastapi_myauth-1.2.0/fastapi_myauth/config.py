import secrets
from typing import Literal

from pydantic import (
    AnyHttpUrl,
    EmailStr,
    field_validator,
)
from pydantic_core.core_schema import FieldValidationInfo
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    TOTP_SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 seconds * 30 minutes = 30 minutes
    ACCESS_TOKEN_EXPIRE_SECONDS: int = 60 * 30
    # 60 seconds * 60 minutes * 24 hours * 30 days = 30 days
    REFRESH_TOKEN_EXPIRE_SECONDS: int = 60 * 60 * 24 * 30
    JWT_ALGO: str = "HS512"
    TOTP_ALGO: Literal["sha1", "sha256", "sha512"] = "sha1"
    FRONTEND_HOST: str = "localhost"
    FRONTEND_URL: AnyHttpUrl = AnyHttpUrl("http://localhost:3000")
    SERVER_BOT: str = "Symona"
    PROJECT_NAME: str = "FastAPI Auth"

    # GENERAL SETTINGS

    MULTI_MAX: int = (
        20  # Maximum number of items returned in a page for CRUD operations
    )

    SMTP_TLS: bool = True
    SMTP_PORT: int | None = None
    SMTP_HOST: str | None = None
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAILS_FROM_EMAIL: EmailStr | None = None
    EMAILS_FROM_NAME: str | None = None
    EMAILS_TO_EMAIL: EmailStr = "a@a.com"

    EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
    EMAIL_TEMPLATES_DIR: str = "/app/app/email-templates/build"
    EMAILS_ENABLED: bool = False

    @field_validator("EMAILS_ENABLED", mode="before")
    @classmethod
    def get_emails_enabled(cls, v: bool, values: FieldValidationInfo) -> bool:
        return bool(
            values.data.get("SMTP_HOST")
            and values.data.get("SMTP_PORT")
            and values.data.get("EMAILS_FROM_EMAIL")
        )

    FIRST_SUPERUSER: EmailStr = "admin@admin.com"
    FIRST_SUPERUSER_PASSWORD: str = "12345678"
    USERS_OPEN_REGISTRATION: bool = True
    EMAIL_TEST_USER: EmailStr = "test@example.com"


settings = Settings()  # pyright: ignore
