# needed for SessionDep and other type hints
# pyright: reportInvalidTypeForm=none

from collections.abc import Callable
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy import Engine
from sqlmodel import Session

from fastapi_myauth import crud, models

from ..config import settings

# This token dependency is static and can be defined at the module level.
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl="/login/oauth")
TokenDep = Annotated[str, Depends(reusable_oauth2)]


class APIDependencies:
    """
    Manages and provides FastAPI dependencies for the authentication system.

    This class encapsulates the logic for creating and accessing dependencies
    like database sessions and authenticated users, making the dependency
    injection system more organized, readable, and type-safe compared to
    using a dictionary.

    An instance of this class is created with a specific CRUD user handler
    and a database session generator. Its methods and properties are then
    used directly in the API router definitions.
    """

    def __init__(
        self,
        crud_user: crud.CRUDUser,
        engine: Engine,
    ):
        """
        Initializes the dependency provider.

        Args:
            crud_user: An instance of the user CRUD handler.
            engine: A SQLAlchemy database engine instance.
        """

        def get_db():
            with Session(engine) as session:
                yield session

        self.crud_user = crud_user
        self.SessionDep = Annotated[Session, Depends(get_db)]

    def get_token_payload(self, token: TokenDep) -> models.TokenPayload:
        """Decodes and validates a JWT, returning its payload."""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO]
            )
            return models.TokenPayload(**payload)
        except (InvalidTokenError, ValidationError) as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            ) from e

    def get_magic_token(self, token: TokenDep) -> models.MagicTokenPayload:
        """Dependency to decode and validate a magic link token."""
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO]
            )
            return models.MagicTokenPayload(**payload)
        except (InvalidTokenError, ValidationError) as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
            ) from e

    @property
    def get_current_user(self) -> Callable[..., models.User]:
        """Factory for the dependency to get a user from a standard access token."""

        def _get_current_user(db: self.SessionDep, token: TokenDep) -> models.User:
            token_data = self.get_token_payload(token)
            if token_data.refresh or token_data.totp:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials, invalid token type.",
                )
            user = self.crud_user.get(db, id=token_data.sub)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            return user

        return _get_current_user

    @property
    def get_totp_user(self) -> Callable[..., models.User]:
        """Factory for the dependency to get a user from a TOTP-purpose access token."""

        def _get_totp_user(db: self.SessionDep, token: TokenDep) -> models.User:
            token_data = self.get_token_payload(token)
            if token_data.refresh or not token_data.totp:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials, invalid token type.",
                )
            user = self.crud_user.get(db, id=token_data.sub)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            return user

        return _get_totp_user

    @property
    def get_refresh_user(self) -> Callable[..., models.User]:
        """Factory for the dependency to get a user from a refresh token, revoking it upon use."""

        def _get_refresh_user(db: self.SessionDep, token: TokenDep) -> models.User:
            token_data = self.get_token_payload(token)
            if not token_data.refresh:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials, not a refresh token.",
                )
            user = self.crud_user.get(db, id=token_data.sub)
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
                )
            if not self.crud_user.is_active(user):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
                )
            # Check and revoke this refresh token
            token_obj = crud.token.get(token=token, user=user)
            if not token_obj:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Could not validate credentials, token revoked or invalid.",
                )
            crud.token.remove(db, db_obj=token_obj)
            return user

        return _get_refresh_user

    @property
    def get_current_active_user(self) -> Callable[..., models.User]:
        """Factory for the dependency to get the current, validated active user."""

        def _get_current_active_user(
            current_user: Annotated[models.User, Depends(self.get_current_user)],
        ) -> models.User:
            if not self.crud_user.is_active(current_user):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
                )
            return current_user

        return _get_current_active_user

    def require_role(self, required_roles: list[str]) -> Callable[..., models.User]:
        """
        Factory for a dependency that checks if a user has one of the required roles.

        This dependency first ensures the user is active, then checks if the user
        is a superuser (who bypasses role checks) or has a role present in the
        `required_roles` list.
        Args:
            required_roles: A list of role strings that are allowed to access the endpoint.
        Returns:
            A dependency function that can be used in FastAPI path operations.
        Raises:
            HTTPException (403): If the user does not have the required privileges.
        """
        CurrentUser = Annotated[models.User, Depends(self.get_current_active_user)]

        def _role_checker(current_user: CurrentUser) -> models.User:
            if self.crud_user.is_superuser(current_user):
                return current_user  # Superusers can do anything
            user_role = getattr(current_user, "role", None)
            if user_role not in required_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="The user does not have the required permissions.",
                )
            return current_user

        return _role_checker

    def get_active_websocket_user(self, db: Session, token: str) -> models.User:
        """
        Validates token and returns an active user for WebSocket connections.

        Note: The `db` session must be provided manually as this is not a standard
        FastAPI dependency for websockets.
        """
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGO]
            )
            token_data = models.TokenPayload(**payload)
        except (InvalidTokenError, ValidationError):
            raise ValidationError("Could not validate credentials")
        if token_data.refresh:
            raise ValidationError("Could not validate credentials")
        user = self.crud_user.get(db, id=token_data.sub)
        if not user:
            raise ValidationError("User not found")
        if not self.crud_user.is_active(user):
            raise ValidationError("Inactive user")
        return user
