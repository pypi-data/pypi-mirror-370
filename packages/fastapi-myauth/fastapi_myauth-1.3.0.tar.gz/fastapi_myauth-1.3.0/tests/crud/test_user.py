from fastapi.encoders import jsonable_encoder
from sqlmodel import Session

from fastapi_myauth.security import verify_password
from fastapi_myauth.test_main import crud_user, fast_auth
from tests.utils.utils import random_email, random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = fast_auth.UserCreate(email=email, password=password, role="editor")
    user = crud_user.create(db=db, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")
    assert hasattr(user, "language")
    assert user.language == "en"
    assert user.role == "editor"


def test_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = fast_auth.UserCreate(email=email, password=password)
    user = crud_user.create(db=db, obj_in=user_in)
    authenticated_user = crud_user.authenticate(db=db, email=email, password=password)
    assert authenticated_user
    assert user.email == authenticated_user.email


def test_not_authenticate_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user = crud_user.authenticate(db=db, email=email, password=password)
    assert user is None


def test_check_if_user_is_active(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = fast_auth.UserCreate(email=email, password=password)
    user = crud_user.create(db=db, obj_in=user_in)
    assert user.is_active is True


def test_check_if_user_is_active_inactive(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = fast_auth.UserCreate(email=email, password=password, is_active=False)
    user = crud_user.create(db=db, obj_in=user_in)
    assert user.is_active is False


def test_check_if_user_is_superuser(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = fast_auth.UserCreate(email=email, password=password, is_superuser=True)
    user = crud_user.create(db=db, obj_in=user_in)
    assert user.is_superuser is True


def test_check_if_user_is_superuser_normal_user(db: Session) -> None:
    username = random_email()
    password = random_lower_string()
    user_in = fast_auth.UserCreate(email=username, password=password)
    user = crud_user.create(db=db, obj_in=user_in)
    assert user.is_superuser is False


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = fast_auth.UserCreate(email=username, password=password, is_superuser=True)
    user = crud_user.create(db=db, obj_in=user_in)
    user_2 = db.get(fast_auth.User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_update_user(db: Session) -> None:
    password = random_lower_string()
    email = random_email()
    user_in = fast_auth.UserCreate(email=email, password=password, is_superuser=True)
    user = crud_user.create(db=db, obj_in=user_in)
    new_password = random_lower_string()
    user_in_update = fast_auth.UserUpdate(
        password=new_password, is_superuser=True, role="editor"
    )
    if user.id is not None:
        crud_user.update(db=db, db_obj=user, obj_in=user_in_update)
    user_2 = db.get(fast_auth.User, user.id)
    assert user_2
    assert user.email == user_2.email
    assert verify_password(
        plain_password=new_password, hashed_password=user_2.hashed_password
    )
    assert user_2.role == "editor"
