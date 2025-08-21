import uuid
from datetime import timedelta
from unittest.mock import patch

from fastapi import status
from fastapi.testclient import TestClient
from freezegun import freeze_time
from pydantic import EmailStr
from sqlmodel import Session

from fastapi_myauth import crud
from fastapi_myauth.config import settings
from fastapi_myauth.security import create_magic_tokens, verify_password
from fastapi_myauth.test_main import crud_user
from tests.utils.user import create_user
from tests.utils.utils import random_email, random_lower_string

# --- Test Data ---
test_email: EmailStr = f"s{settings.EMAIL_TEST_USER}"
test_password: str = random_lower_string()
test_full_name: str = "Test User"

# --- Test Cases ---

# ===========================
# 1. Signup Endpoint (/login/signup)
# ===========================


def test_create_user_profile_success(client: TestClient, db: Session, monkeypatch):
    """Test successful user creation."""
    monkeypatch.setattr(settings, "USERS_OPEN_REGISTRATION", True)
    data = {
        "email": test_email,
        "password": test_password,
        "full_name": test_full_name,
    }
    response = client.post("/login/signup", json=data)
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["email"] == test_email
    assert content["full_name"] == test_full_name
    assert "id" in content
    assert isinstance(
        content.get("hashed_password"), bool
    )  # Ensure it returns a boolean and not the actual hashed password

    # Verify user exists in DB (optional but good)
    user = crud_user.get_by_email(db, email=test_email)
    assert user is not None
    assert user.email == test_email
    assert user.full_name == test_full_name


def test_create_user_profile_duplicate_email(
    client: TestClient, db: Session, monkeypatch
):
    """Test user creation failure with a duplicate email."""
    monkeypatch.setattr(settings, "USERS_OPEN_REGISTRATION", True)
    # Create a user first
    create_user(db=db, email=test_email)

    data = {"email": test_email, "password": test_password}
    response = client.post("/login/signup", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "not available" in content["detail"]


def test_create_user_profile_registration_closed(client: TestClient, monkeypatch):
    """Test user creation failure when registration is closed."""
    monkeypatch.setattr(settings, "USERS_OPEN_REGISTRATION", False)
    data = {"email": f"closed_{test_email}", "password": test_password}
    response = client.post("/login/signup", json=data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "Registration is closed" in content["detail"]


# ===================================
# 2. Magic Link Login (/login/magic/{email})
# ===================================


@patch("fastapi_myauth.api.v1.login.send_magic_login_email")
def test_login_with_magic_link_existing_user(
    mock_send_email, client: TestClient, db: Session, monkeypatch
):
    """Test magic link generation for an existing, active user."""
    monkeypatch.setattr(settings, "EMAILS_ENABLED", True)
    user = create_user(db=db)
    assert user.email is not None

    response = client.post(f"/login/magic/{user.email}")
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "claim" in content
    assert isinstance(content["claim"], str)
    # Verify email was called
    mock_send_email.assert_called_once()
    call_args, call_kwargs = mock_send_email.call_args
    assert call_kwargs["email_to"] == user.email
    assert "token" in call_kwargs


@patch("fastapi_myauth.api.v1.login.send_magic_login_email")
def test_login_with_magic_link_new_user_registration_open(
    mock_send_email, client: TestClient, db: Session, monkeypatch
):
    """Test magic link generation for a new user when registration is open."""
    monkeypatch.setattr(settings, "USERS_OPEN_REGISTRATION", True)
    monkeypatch.setattr(settings, "EMAILS_ENABLED", True)
    new_email = random_email()

    response = client.post(f"/login/magic/{new_email}")
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "claim" in content

    # Verify user was created
    user = crud_user.get_by_email(db, email=new_email)
    assert user is not None
    assert user.email == new_email
    assert not user.email_validated  # Should not be validated yet

    # Verify email was called
    mock_send_email.assert_called_once()
    call_args, call_kwargs = mock_send_email.call_args
    assert call_kwargs["email_to"] == new_email


def test_login_with_magic_link_new_user_registration_closed(
    client: TestClient, db: Session, monkeypatch
):
    """Test magic link failure for a new user when registration is closed."""
    monkeypatch.setattr(settings, "USERS_OPEN_REGISTRATION", False)
    new_email = random_email()

    response = client.post(f"/login/magic/{new_email}")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "Registration is closed" in content["detail"]

    # Verify user was not created
    user = crud_user.get_by_email(db, email=new_email)
    assert user is None


@patch("fastapi_myauth.api.v1.login.send_magic_login_email")
def test_login_with_magic_link_inactive_user(
    mock_send_email, client: TestClient, db: Session, monkeypatch
):
    """Test magic link failure for an inactive user (should still pretend to send)."""
    monkeypatch.setattr(settings, "USERS_OPEN_REGISTRATION", True)
    monkeypatch.setattr(settings, "EMAILS_ENABLED", True)
    user = create_user(db=db, is_active=False)
    assert user.email is not None

    response = client.post(f"/login/magic/{user.email}")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "activate your account" in content["detail"]

    # Verify user was created but email wasn't sent
    user = crud_user.get_by_email(db, email=user.email)
    assert user is not None
    mock_send_email.assert_not_called()


# ============================
# 3. Claim Magic Link (/login/claim)
# ============================


def test_validate_magic_link_success(client: TestClient, db: Session):
    """Test successful validation of a magic link."""
    user = create_user(db=db, email_validated=False)
    assert user.id is not None

    # Generate real magic tokens
    email_token, claim_token = create_magic_tokens(subject=user.id)

    data = {"claim": claim_token}
    response = client.post(
        "/login/claim",
        headers={"Authorization": f"Bearer {email_token}"},
        json=data,
    )

    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "access_token" in content
    assert "refresh_token" in content
    assert content["token_type"] == "bearer"

    # Verify email is now validated
    db.refresh(user)
    assert user.email_validated is True

    # Verify refresh token created in DB
    token_in_db = crud.token.get(user=user, token=content["refresh_token"])
    assert token_in_db is not None
    assert token_in_db.authenticates_id == user.id


def test_validate_magic_link_invalid_mail_token(client: TestClient, db: Session):
    """Test magic link validation failure with an invalid mail token."""
    user = create_user(db=db)
    assert user.id is not None

    # Generate real magic tokens
    _, claim_token = create_magic_tokens(subject=user.id)

    data = {"claim": claim_token}
    response = client.post(
        "/login/claim",
        headers={"Authorization": "Bearer invalid_token"},
        json=data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_validate_magic_link_invalid_claim_token(client: TestClient, db: Session):
    """Test magic link validation failure with an invalid claim token."""
    user = create_user(db=db)
    assert user.id is not None

    # Generate real magic tokens
    email_token, _ = create_magic_tokens(subject=user.id)

    data = {"claim": "invalid_claim_token"}
    response = client.post(
        "/login/claim",
        headers={"Authorization": f"Bearer {email_token}"},
        json=data,
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_validate_magic_link_different_tokens(client: TestClient, db: Session):
    """Test magic link validation failure with different token subs."""
    user1 = create_user(db=db, email="user1@example.com")
    assert user1.id is not None
    user2 = create_user(db=db, email="user2@example.com")
    assert user2.id is not None

    # Generate real magic tokens
    email_token, _ = create_magic_tokens(subject=user1.id)
    _, claim_token = create_magic_tokens(subject=user2.id)

    data = {"claim": claim_token}
    response = client.post(
        "/login/claim",
        headers={"Authorization": f"Bearer {email_token}"},
        json=data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "invalid claim" in content["detail"]


def test_validate_magic_link_inactive_user(client: TestClient, db: Session):
    """Test magic link validation failure for an inactive user."""
    user = create_user(db=db, is_active=False)
    assert user.id is not None

    email_token, claim_token = create_magic_tokens(subject=user.id)
    data = {"claim": claim_token}
    response = client.post(
        "/login/claim",
        headers={"Authorization": f"Bearer {email_token}"},
        json=data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "invalid claim" in content["detail"]


def test_validate_magic_link_user_not_found(client: TestClient):
    """Test magic link validation failure when user ID in token doesn't exist."""
    non_existent_user_id = uuid.uuid4()
    email_token, claim_token = create_magic_tokens(subject=non_existent_user_id)
    data = {"claim": claim_token}
    response = client.post(
        "/login/claim",
        headers={"Authorization": f"Bearer {email_token}"},
        json=data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "invalid claim" in content["detail"]


# ========================
# 4. OAuth2 Login (/oauth)
# ========================


def test_login_with_oauth2_success(client: TestClient, db: Session):
    """Test successful login with username/password."""
    user = create_user(db=db, password=test_password)
    assert user.email is not None

    login_data = {"username": user.email, "password": test_password}
    response = client.post("/login/oauth", data=login_data)  # Form data

    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "access_token" in content
    assert "refresh_token" in content
    assert content["token_type"] == "bearer"

    # Verify refresh token created in DB
    token_in_db = crud.token.get(user=user, token=content["refresh_token"])
    assert token_in_db is not None
    assert token_in_db.authenticates_id == user.id


def test_login_with_oauth2_incorrect_password(client: TestClient, db: Session):
    """Test login failure with incorrect password."""
    user = create_user(db=db, password=test_password)
    assert user.email is not None

    login_data = {"username": user.email, "password": "wrongpassword"}
    response = client.post("/login/oauth", data=login_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "incorrect email or password" in content["detail"]  # Generic message


def test_login_with_oauth2_user_not_found(client: TestClient):
    """Test login failure with non-existent email."""
    login_data = {"username": "nosuchuser@example.com", "password": "somepassword"}
    response = client.post("/login/oauth", data=login_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "incorrect email or password" in content["detail"]  # Generic message


def test_login_with_oauth2_inactive_user(client: TestClient, db: Session):
    """Test login failure for an inactive user."""
    user = create_user(db=db, password=test_password, is_active=False)
    assert user.email is not None

    login_data = {"username": user.email, "password": test_password}
    response = client.post("/login/oauth", data=login_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "incorrect email or password" in content["detail"]  # Generic message


# ====================================================================
# 5. TOTP Endpoints (/new-totp, /totp[POST], /totp[PUT], /totp[DELETE])
# ====================================================================
# Note: These tests require more setup involving authenticated users and potentially
# mocking TOTP generation/verification or using a library like pyotp.


def test_request_new_totp(
    client: TestClient, normal_user_token_headers: dict[str, str]
):
    """Test requesting new TOTP details."""
    response = client.post("/login/new-totp", headers=normal_user_token_headers)
    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "uri" in content
    assert "secret" not in content
    assert "key" in content


# Tests for /totp POST, PUT, DELETE would follow a similar pattern:
# - Create a user.
# - Get authentication headers (likely need standard access token first).
# - For PUT/DELETE, potentially mock `crud_user.authenticate`.
# - Mock `security.verify_totp` or use a real TOTP library to generate codes.
# - Make the request with appropriate data (TOTP code, password if needed).
# - Assert status code, response message, and DB changes (totp_secret, totp_counter).

# ===========================
# 6. Token Refresh (/refresh)
# ===========================


def test_refresh_token_success(client: TestClient, db: Session):
    """Test successful token refresh."""
    # 1. Login to get initial tokens including a refresh token
    user = create_user(db=db, password=test_password)
    assert user.email is not None
    login_data = {"username": user.email, "password": test_password}

    initial_time = "2023-01-01 12:00:00"
    with freeze_time(initial_time) as freezer:
        login_response = client.post("/login/oauth", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        initial_tokens = login_response.json()
        refresh_token = initial_tokens["refresh_token"]
        initial_access_token = initial_tokens["access_token"]

        # --- Step 2: Advance time before refreshing ---
        freezer.tick(delta=timedelta(seconds=5))

        # --- Step 3: Refresh the token at the advanced time ---
        refresh_headers = {"Authorization": f"Bearer {refresh_token}"}
        refresh_response = client.post("/login/refresh", headers=refresh_headers)

    # --- Step 4: Assertions ---
    assert refresh_response.status_code == status.HTTP_200_OK
    new_tokens = refresh_response.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["token_type"] == "bearer"
    assert new_tokens["access_token"] != initial_access_token
    assert new_tokens["refresh_token"] != refresh_token

    # Verify new refresh token created in DB
    new_token_in_db = crud.token.get(user=user, token=new_tokens["refresh_token"])
    assert new_token_in_db is not None
    assert new_token_in_db.authenticates_id == user.id

    old_token_in_db = crud.token.get(user=user, token=refresh_token)
    assert old_token_in_db is None


def test_refresh_token_invalid_token(client: TestClient):
    """Test token refresh failure with an invalid token."""
    refresh_headers = {"Authorization": "Bearer invalid-refresh-token"}
    response = client.post("/login/refresh", headers=refresh_headers)
    # The dependency get_refresh_user should handle this
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert (
        "Could not validate credentials" in content["detail"]
    )  # Or similar standard FastAPISecurity error


# =========================
# 7. Revoke Token (/revoke)
# =========================


def test_revoke_token_success(client: TestClient, db: Session):
    """Test successful token revocation."""
    user = create_user(db=db, password=test_password)
    assert user.email is not None
    login_data = {"username": user.email, "password": test_password}
    login_response = client.post("/login/oauth", data=login_data)
    assert login_response.status_code == status.HTTP_200_OK
    refresh_token = login_response.json()["refresh_token"]

    revoke_headers = {"Authorization": f"Bearer {refresh_token}"}
    revoke_response = client.post("/login/revoke", headers=revoke_headers)

    assert revoke_response.status_code == status.HTTP_200_OK
    content = revoke_response.json()
    assert content["msg"] == "Token revoked successfully."

    refresh_again_response = client.post("/login/refresh", headers=revoke_headers)
    assert refresh_again_response.status_code == status.HTTP_403_FORBIDDEN
    content = refresh_again_response.json()
    assert "Could not validate credentials" in content["detail"]

    token_in_db = crud.token.get(token=refresh_token, user=user)
    assert token_in_db is None


def test_revoke_token_invalid_token(client: TestClient):
    """Test token revoke failure with an invalid token."""
    revoke_headers = {"Authorization": "Bearer invalid-refresh-token"}
    response = client.post("/login/revoke", headers=revoke_headers)
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert "Could not validate credentials" in content["detail"]


# ======================================
# 8. Password Recovery (/recover/{email})
# ======================================


@patch("fastapi_myauth.api.v1.login.send_reset_password_email")
def test_recover_password_existing_user(
    mock_send_email, client: TestClient, db: Session, monkeypatch
):
    """Test password recovery request for an existing, active user."""
    monkeypatch.setattr(settings, "EMAILS_ENABLED", True)
    user = create_user(db=db)
    assert user.email is not None

    response = client.post(f"/login/recover/{user.email}")

    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "claim" in content  # Returns the claim token
    mock_send_email.assert_called_once()
    args, kwargs = mock_send_email.call_args
    assert kwargs["email_to"] == user.email
    assert kwargs["email"] == user.email
    assert "token" in kwargs  # Check that a token was passed for the email


def test_recover_password_non_existent_user(client: TestClient, monkeypatch):
    """Test password recovery request for a non-existent user (generic response)."""
    monkeypatch.setattr(
        settings, "EMAILS_ENABLED", True
    )  # Still need this true for consistent flow if logic doesn't branch early
    non_existent_email = "nosuchrecover@example.com"
    response = client.post(f"/login/recover/{non_existent_email}")

    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert "If that login exists" in content["msg"]


@patch("fastapi_myauth.api.v1.login.send_reset_password_email")
def test_recover_password_inactive_user(
    mock_send_email, client: TestClient, db: Session, monkeypatch
):
    """Test password recovery for an inactive user (generic response)."""
    monkeypatch.setattr(settings, "EMAILS_ENABLED", True)
    user = create_user(db=db, is_active=False)
    assert user.email is not None

    response = client.post(f"/login/recover/{user.email}")

    assert response.status_code == status.HTTP_200_OK  # Should return OK
    content = response.json()
    assert "If that login exists" in content["msg"]  # Generic message
    mock_send_email.assert_not_called()  # Email should not be sent


# ==========================
# 9. Reset Password (/reset)
# ==========================


def test_reset_password_success(client: TestClient, db: Session):
    """Test successful password reset using a valid claim token."""
    user = create_user(db=db)
    assert user.id is not None
    original_hashed_password = user.hashed_password

    # Generate real magic tokens (for reset)
    email_token, claim_token = create_magic_tokens(subject=user.id)

    data = {"new_password": test_password, "claim": claim_token}
    response = client.post(
        "/login/reset",
        headers={"Authorization": f"Bearer {email_token}"},
        json=data,
    )

    assert response.status_code == status.HTTP_200_OK
    content = response.json()
    assert content["msg"] == "Password updated successfully."

    # Verify password changed in DB
    db.refresh(user)
    assert user.hashed_password != original_hashed_password
    assert verify_password(
        plain_password=test_password, hashed_password=user.hashed_password
    )


def test_reset_password_invalid_mail_token(client: TestClient, db: Session):
    """Test password reset failure with an invalid mail token."""
    user = create_user(db=db)
    assert user.id is not None

    # Generate real magic tokens
    _, claim_token = create_magic_tokens(subject=user.id)

    data = {"new_password": test_password, "claim": claim_token}
    response = client.post(
        "/login/reset",
        headers={"Authorization": "Bearer invalid_token"},
        json=data,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_reset_password_invalid_claim_token(client: TestClient, db: Session):
    """Test password reset failure with an invalid claim token."""
    user = create_user(db=db)
    assert user.id is not None

    # Generate real magic tokens
    email_token, _ = create_magic_tokens(subject=user.id)

    data = {"new_password": test_password, "claim": "invalid_claim_token"}
    response = client.post(
        "/login/reset",
        headers={"Authorization": f"Bearer {email_token}"},
        json=data,
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_reset_password_different_tokens(client: TestClient, db: Session):
    """Test password reset failure with with different token subs."""
    user1 = create_user(db=db, email="user1@example.com")
    assert user1.id is not None
    user2 = create_user(db=db, email="user2@example.com")
    assert user2.id is not None

    # Generate real magic tokens
    email_token, _ = create_magic_tokens(subject=user1.id)
    _, claim_token = create_magic_tokens(subject=user2.id)

    data = {"new_password": test_password, "claim": claim_token}
    response = client.post(
        "/login/reset",
        headers={"Authorization": f"Bearer {email_token}"},
        json=data,
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "invalid claim" in content["detail"]


def test_reset_password_inactive_user(client: TestClient, db: Session):
    """Test password reset failure when the user is inactive."""
    user = create_user(db=db, is_active=False)
    assert user.id is not None

    email_token, claim_token = create_magic_tokens(subject=user.id)
    data = {"new_password": test_password, "claim": claim_token}
    response = client.post(
        "/login/reset",
        headers={"Authorization": f"Bearer {email_token}"},
        json=data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "invalid claim" in content["detail"]


def test_reset_password_user_not_found(client: TestClient):
    """Test password reset failure when user ID in token doesn't exist."""
    non_existent_user_id = uuid.uuid4()
    email_token, claim_token = create_magic_tokens(subject=non_existent_user_id)
    data = {"new_password": test_password, "claim": claim_token}
    response = client.post(
        "/login/reset",
        headers={"Authorization": f"Bearer {email_token}"},
        json=data,
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    content = response.json()
    assert "invalid claim" in content["detail"]


# ==========================
# 10. Token Expiration
# ==========================


def test_access_token_expiration(client: TestClient, db: Session):
    """Test that an expired access token is rejected."""
    user = create_user(db=db, password=test_password)
    assert user.email is not None
    login_data = {"username": user.email, "password": test_password}

    # 1. Login to get a valid access token
    initial_time = "2023-01-01 10:00:00"
    with freeze_time(initial_time) as freezer:
        login_response = client.post("/login/oauth", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        initial_tokens = login_response.json()
        access_token = initial_tokens["access_token"]

        # 2. Advance time past the token's expiration
        expires_delta_seconds = settings.ACCESS_TOKEN_EXPIRE_SECONDS
        freezer.tick(delta=timedelta(seconds=expires_delta_seconds + 1))

        # 3. Attempt to use the expired access token
        expired_headers = {"Authorization": f"Bearer {access_token}"}
        response = client.post("/login/new-totp", headers=expired_headers)

    # 4. Assert rejection due to expiration
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert "not validate credentials" in content["detail"]


def test_refresh_token_expiration(client: TestClient, db: Session):
    """Test that an expired refresh token is rejected."""
    user = create_user(db=db, password=test_password)
    assert user.email is not None
    login_data = {"username": user.email, "password": test_password}

    # 1. Login to get a valid refresh token
    initial_time = "2023-01-02 11:00:00"
    with freeze_time(initial_time) as freezer:
        login_response = client.post("/login/oauth", data=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        initial_tokens = login_response.json()
        refresh_token = initial_tokens["refresh_token"]

        # 2. Advance time past the refresh token's expiration
        expires_delta_seconds = settings.REFRESH_TOKEN_EXPIRE_SECONDS
        freezer.tick(delta=timedelta(seconds=expires_delta_seconds + 1))

        # 3. Attempt to use the expired refresh token
        expired_headers = {"Authorization": f"Bearer {refresh_token}"}
        response = client.post("/login/refresh", headers=expired_headers)

    # 4. Assert rejection due to expiration
    assert response.status_code == status.HTTP_403_FORBIDDEN
    content = response.json()
    assert "not validate credentials" in content["detail"]
