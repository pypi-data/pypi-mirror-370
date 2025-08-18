from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, delete

from fastapi_myauth.config import settings
from fastapi_myauth.models import RefreshToken
from fastapi_myauth.test_main import app, engine, fast_auth, init_db
from tests.utils.user import authentication_token_from_email


@pytest.fixture()
def db() -> Generator[Session]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(RefreshToken)
        session.execute(statement)
        statement = delete(fast_auth.User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def superuser_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, db=db, email=settings.EMAIL_TEST_USER, is_superuser=True
    )


@pytest.fixture()
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, db=db, email=settings.EMAIL_TEST_USER
    )
