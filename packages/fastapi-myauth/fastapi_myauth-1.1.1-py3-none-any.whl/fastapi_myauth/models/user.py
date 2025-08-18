from datetime import datetime
from uuid import UUID, uuid4

from pydantic import EmailStr, field_validator
from sqlmodel import Field, SQLModel


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(index=True, unique=True, max_length=255)
    role: str | None = Field(default="user")
    email_validated: bool = False
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str | None = Field(default=None, min_length=8, max_length=64)


# Properties to receive via API on update
class UserUpdate(UserBase):
    email: EmailStr | None = None
    original: str | None = Field(default=None, min_length=8, max_length=64)
    password: str | None = Field(default=None, min_length=8, max_length=64)


# Additional properties to return via API
class UserRead(UserBase):
    id: UUID
    hashed_password: bool = Field(default=False, alias="password")
    totp_secret: bool = Field(default=False, alias="totp")
    created: datetime
    modified: datetime

    @field_validator("hashed_password", mode="before")
    @classmethod
    def evaluate_hashed_password(cls, hashed_password):
        if hashed_password:
            return True
        return False

    @field_validator("totp_secret", mode="before")
    @classmethod
    def evaluate_totp_secret(cls, totp_secret):
        if totp_secret:
            return True
        return False


class User(UserBase, table=False):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    modified: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={
            "onupdate": datetime.utcnow,
        },
    )
    hashed_password: str | None = Field(default=None)
    totp_secret: str | None = Field(default=None)
    totp_counter: int | None = Field(default=None)
