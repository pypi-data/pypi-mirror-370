from dataclasses import dataclass, field
from typing import Generic, TypeVar

from fastapi import APIRouter
from sqlalchemy import Engine
from sqlmodel import Relationship

from . import crud, models
from .api.deps import APIDependencies

# Generic type variables for user models
UserT = TypeVar("UserT", bound=models.User)
UserReadT = TypeVar("UserReadT", bound=models.UserRead)
UserCreateT = TypeVar("UserCreateT", bound=models.UserCreate)
UserUpdateT = TypeVar("UserUpdateT", bound=models.UserUpdate)


@dataclass
class AuthModels(Generic[UserT, UserReadT, UserCreateT, UserUpdateT]):
    """
    A container for the user-related models.

    This class handles the dynamic creation of the internal User model
    by adding the necessary relationships for the authentication system.
    """

    user_model: type[UserT] = models.User  # type: ignore[assignment]
    user_read: type[UserReadT] = models.UserRead  # type: ignore[assignment]
    user_create: type[UserCreateT] = models.UserCreate  # type: ignore[assignment]
    user_update: type[UserUpdateT] = models.UserUpdate  # type: ignore[assignment]

    _internal_user_model: type[UserT] = field(init=False)

    def __post_init__(self):
        """
        Dynamically creates the internal User model with relationships
        after the instance has been initialized.
        """

        class User(self.user_model, table=True):  # type: ignore
            refresh_tokens: list[models.RefreshToken] = Relationship(
                back_populates="authenticates", cascade_delete=True
            )

        self._internal_user_model = User  # type: ignore

    @property
    def User(self) -> type[UserT]:
        """Returns the fully configured internal user model."""
        return self._internal_user_model

    @property
    def UserRead(self) -> type[UserReadT]:
        """Returns the user read model."""
        return self.user_read

    @property
    def UserCreate(self) -> type[UserCreateT]:
        """Returns the user create model."""
        return self.user_create

    @property
    def UserUpdate(self) -> type[UserUpdateT]:
        """Returns the user update model."""
        return self.user_update


@dataclass
class FastAuth(Generic[UserT, UserReadT, UserCreateT, UserUpdateT]):
    """
    FastAPI Authentication class.

    This class takes an engine and a pre-configured AuthModels instance
    to set up the authentication routes and dependencies.
    """

    engine: Engine
    models: AuthModels[UserT, UserReadT, UserCreateT, UserUpdateT]

    _crud_user_instance: crud.CRUDUser[UserT, UserCreateT, UserUpdateT] = field(
        init=False
    )
    _deps_instance: APIDependencies = field(init=False)

    def __post_init__(self):
        """
        Initializes the CRUD and dependency injection layers using the
        provided models.
        """

        # Dynamically create a CRUD class with the fully-configured models
        class CrudUser(crud.CRUDUser[self.User, self.UserCreate, self.UserUpdate]):  # type: ignore
            pass

        self._crud_user_instance = CrudUser(self.User)

        self._deps_instance = APIDependencies(
            crud_user=self._crud_user_instance,
            engine=self.engine,
        )

    @property
    def User(self) -> type[UserT]:
        """Returns the fully configured internal user model."""
        return self.models.User

    @property
    def UserRead(self) -> type[UserReadT]:
        """Returns the user read model."""
        return self.models.UserRead

    @property
    def UserCreate(self) -> type[UserCreateT]:
        """Returns the user create model."""
        return self.models.UserCreate

    @property
    def UserUpdate(self) -> type[UserUpdateT]:
        """Returns the user update model."""
        return self.models.UserUpdate

    @property
    def crud_user(self) -> crud.CRUDUser[UserT, UserCreateT, UserUpdateT]:
        """Returns the CRUD user handler."""
        return self._crud_user_instance

    @property
    def deps(self) -> APIDependencies:
        """Returns the dependency provider for the auth library."""
        return self._deps_instance

    def get_router(self) -> APIRouter:
        """
        Constructs and returns a pre-configured APIRouter with all auth routes.
        """
        from fastapi_myauth.api.v1 import get_login_router, get_user_router

        api_router = APIRouter()
        deps_instance = self.deps

        api_router.include_router(
            get_user_router(
                crud_user=self.crud_user,
                deps=deps_instance,
                user_model=self.User,
                user_read=self.UserRead,
                user_create=self.UserCreate,
                user_update=self.UserUpdate,
            ),
            prefix="/users",
            tags=["users"],
        )
        api_router.include_router(
            get_login_router(
                crud_user=self.crud_user,
                deps=deps_instance,
                user_model=self.User,
                user_read=self.UserRead,
                user_create=self.UserCreate,
                user_update=self.UserUpdate,
            ),
            prefix="/login",
            tags=["login"],
        )

        return api_router
