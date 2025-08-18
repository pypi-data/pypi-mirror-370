from typing import TYPE_CHECKING
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class RefreshTokenBase(SQLModel):
    token: str = Field(primary_key=True)
    authenticates_id: UUID = Field(foreign_key="user.id")


class RefreshTokenCreate(RefreshTokenBase):
    pass


class RefreshTokenUpdate(RefreshTokenBase):
    pass


class RefreshToken(RefreshTokenBase, table=True):
    authenticates: "User" = Relationship(back_populates="refresh_tokens")


class Token(SQLModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str


class TokenPayload(SQLModel):
    sub: UUID | None = None
    refresh: bool | None = False
    totp: bool | None = False


class MagicTokenPayload(SQLModel):
    sub: UUID | None = None
    fingerprint: UUID | None = None


class WebToken(SQLModel):
    claim: str
