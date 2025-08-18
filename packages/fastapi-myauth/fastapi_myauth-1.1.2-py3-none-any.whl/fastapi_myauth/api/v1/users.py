# needed for SessionDep and other type hints
# pyright: reportInvalidTypeForm=none

from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Path, status
from pydantic import EmailStr

from fastapi_myauth import crud, models
from fastapi_myauth.api.deps import APIDependencies
from fastapi_myauth.config import settings
from fastapi_myauth.email import (
    send_new_account_email,
)


def get_user_router(
    crud_user: crud.crud_user.CRUDUser,
    deps: APIDependencies,
    user_model: type[models.User],
    user_read: type[models.UserRead],
    user_create: type[models.UserCreate],
    user_update: type[models.UserUpdate],
) -> APIRouter:
    router = APIRouter()
    SessionDep = deps.SessionDep

    @router.put("/me", response_model=user_read)
    def update_user_me(
        *,
        db: SessionDep,
        obj_in: user_update,
        current_user: Annotated[user_model, Depends(deps.get_current_active_user)],
    ) -> Any:
        """
        Update user.
        """
        if current_user.hashed_password:
            user = crud_user.authenticate(
                db, email=current_user.email, password=obj_in.original
            )
            if not obj_in.original or not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to authenticate this update.",
                )
        user_in = user_update.model_validate(current_user)
        if obj_in.password is not None:
            user_in.password = obj_in.password
        if obj_in.full_name is not None:
            user_in.full_name = obj_in.full_name
        if obj_in.email is not None:
            check_user = crud_user.get_by_email(db, email=obj_in.email)
            if check_user and check_user.email != current_user.email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This username is not available.",
                )
            user_in.email = obj_in.email
        user = crud_user.update(db, db_obj=current_user, obj_in=user_in)
        return user

    @router.get("/me", response_model=user_read)
    def read_user_me(
        *,
        current_user: Annotated[user_model, Depends(deps.get_current_active_user)],
    ) -> Any:
        """
        Get current user.
        """
        return current_user

    @router.delete("/me", response_model=models.Msg)
    def delete_user_me(
        db: SessionDep,
        current_user: Annotated[user_model, Depends(deps.get_current_active_user)],
    ) -> Any:
        """
        Delete own user.
        """
        if current_user.is_superuser:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Super users are not allowed to delete themselves",
            )
        crud_user.remove(db, id=current_user.id)
        return models.Msg(msg="User deleted successfully")

    @router.get(
        "/",
        response_model=list[user_read],
        dependencies=[Depends(deps.require_role(["admin"]))],
    )
    def read_all_users(
        *,
        db: SessionDep,
        page: int = 0,
    ) -> Any:
        """
        Retrieve all current users.
        """
        return crud_user.get_multi(db=db, page=page)

    @router.post(
        "/toggle-state",
        response_model=models.Msg,
        dependencies=[Depends(deps.require_role(["admin"]))],
    )
    def toggle_state(
        *,
        db: SessionDep,
        user_email: Annotated[EmailStr, Body(embed=True)],
    ) -> Any:
        """
        Toggle user state (moderator function)
        """
        response = crud_user.toggle_user_state(db=db, user_email=user_email)
        if not response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request.",
            )
        return {"msg": "User state toggled successfully."}

    @router.post(
        "/create",
        response_model=user_read,
        dependencies=[Depends(deps.require_role(["admin"]))],
    )
    def create_user(
        *,
        db: SessionDep,
        user_in: user_create,
    ) -> Any:
        """
        Create new user (moderator function).
        """
        user = crud_user.get_by_email(db, email=user_in.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="The user with this username already exists in the system.",
            )
        user = crud_user.create(db, obj_in=user_in)
        if settings.EMAILS_ENABLED and user_in.email:
            send_new_account_email(email_to=user_in.email, username=user_in.email)
        return user

    @router.get(
        "/{user_id}",
        response_model=user_read,
        dependencies=[Depends(deps.require_role(["admin"]))],
    )
    def read_user_by_id(
        user_id: Annotated[UUID, Path(title="The ID of the user to get")],
        db: SessionDep,
    ) -> Any:
        """
        Get a specific user by id. (moderator function)
        """
        user = db.get(user_model, user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        return user

    @router.post(
        "/{user_id}",
        response_model=user_read,
        dependencies=[Depends(deps.require_role(["admin"]))],
    )
    def update_user_by_id(
        *,
        user_id: Annotated[UUID, Path(title="The ID of the user to update")],
        db: SessionDep,
        user_in: user_update,
    ) -> Any:
        """
        Modify user (moderator function)
        """
        db_obj = crud_user.get(db, id=user_id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        if user_in.email:
            check_user = crud_user.get_by_email(db, email=user_in.email)
            if check_user and check_user.email != db_obj.email:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This username is not available.",
                )
        user = crud_user.update(db, db_obj=db_obj, obj_in=user_in)
        return user

    @router.delete(
        "/{user_id}",
        response_model=models.Msg,
        dependencies=[Depends(deps.require_role(["admin"]))],
    )
    def delete_user_by_id(
        *,
        user_id: Annotated[UUID, Path(title="The ID of the user to delete")],
        db: SessionDep,
    ) -> Any:
        """
        Delete user (moderator function)
        """
        db_obj = crud_user.get(db, id=user_id)
        if not db_obj:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found.",
            )
        crud_user.remove(db, id=db_obj.id)
        return models.Msg(msg="User deleted successfully.")

    return router
