from uuid import uuid4

from fastapi.testclient import TestClient
from pydantic import EmailStr
from sqlmodel import Session

from fastapi_myauth import models
from fastapi_myauth.config import settings
from fastapi_myauth.security import verify_password
from fastapi_myauth.test_main import crud_user, fast_auth
from tests.utils.user import create_user, user_authentication_headers
from tests.utils.utils import random_email, random_lower_string


# Helper function to get user from DB for verification
def get_user_by_email(db: Session, email: EmailStr) -> models.User | None:
    return crud_user.get_by_email(db=db, email=email)


# ===========================
# 1. Update User (/me) Endpoint
# ===========================


def test_update_user_me_success_full_name(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test successful update of the current user's full_name.
    """
    original_email = settings.EMAIL_TEST_USER
    original_password = "changeme"
    new_full_name = random_lower_string(10)

    update_data = {
        "original": original_password,
        "full_name": new_full_name,
        # email and password not provided, should remain unchanged
    }
    response = client.put(
        "/users/me",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    updated_user_data = response.json()
    assert updated_user_data["email"] == original_email
    assert updated_user_data["full_name"] == new_full_name
    assert isinstance(
        updated_user_data.get("hashed_password"), bool
    )  # Ensure it returns a boolean and not the actual hashed password
    db_user = get_user_by_email(db, original_email)
    assert db_user is not None
    assert db_user.full_name == new_full_name
    # Verify password hasn't changed by trying to authenticate with original
    login_data = {"username": original_email, "password": original_password}
    r = client.post("/login/oauth", data=login_data)
    assert r.status_code == 200


def test_update_user_me_success_email(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test successful update of the current user's email.
    """
    original_email = settings.EMAIL_TEST_USER
    original_password = "changeme"
    new_email = random_email()

    update_data = {
        "original": original_password,
        "email": new_email,
    }
    response = client.put(
        "/users/me",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    updated_user_data = response.json()
    assert updated_user_data["email"] == new_email

    # Verify old email no longer works
    db_user_old = get_user_by_email(db, original_email)
    assert db_user_old is None
    # Verify new email exists in DB
    db_user_new = get_user_by_email(db, new_email)
    assert db_user_new is not None
    assert db_user_new.email == new_email

    # Verify login with new email
    login_data = {"username": new_email, "password": original_password}
    r = client.post("/login/oauth", data=login_data)
    assert r.status_code == 200


def test_update_user_me_success_password(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test successful update of the current user's password.
    """
    original_email = settings.EMAIL_TEST_USER
    original_password = "changeme"
    new_password = random_lower_string(12)

    update_data = {
        "original": original_password,
        "password": new_password,
    }
    response = client.put(
        "/users/me",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    updated_user_data = response.json()
    assert updated_user_data["email"] == original_email

    # Verify login with new password
    login_data_new = {"username": original_email, "password": new_password}
    r_new = client.post("/login/oauth", data=login_data_new)
    assert r_new.status_code == 200

    # Verify login with old password fails
    login_data_old = {"username": original_email, "password": original_password}
    r_old = client.post("/login/oauth", data=login_data_old)
    assert r_old.status_code == 400


def test_update_user_me_incorrect_original_password(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test updating user /me with an incorrect original password.
    """
    wrong_password = random_lower_string()
    update_data = {
        "original": wrong_password,
        "full_name": "Any Name",
    }
    response = client.put(
        "/users/me",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert response.status_code == 400
    assert "Unable to authenticate this update" in response.json()["detail"]


def test_update_user_me_email_conflict(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test updating user /me email to an email already taken by another user.
    """
    # Create another user first
    existing_user_email = random_email()
    create_user(db, email=existing_user_email)

    original_password = "changeme"
    update_data = {
        "original": original_password,
        "email": existing_user_email,  # Try to use the other user's email
    }
    response = client.put(
        "/users/me",
        headers=normal_user_token_headers,
        json=update_data,
    )
    assert response.status_code == 409
    assert "username is not available" in response.json()["detail"]


def test_update_user_me_unauthenticated(client: TestClient) -> None:
    """
    Test updating user /me without authentication.
    """
    update_data = {"original": "any", "full_name": "Any Name"}
    response = client.put(
        "/users/me",
        json=update_data,  # No headers
    )
    assert response.status_code == 401  # Expect Unauthorized


# ===========================
# 2. Get User (/me) Endpoint
# ===========================


def test_read_user_me_success(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test successful retrieval of the current user's details.
    """
    response = client.get(
        "/users/me",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["email"] == settings.EMAIL_TEST_USER
    assert user_data["is_active"] is True
    assert user_data["is_superuser"] is False
    assert isinstance(
        user_data.get("hashed_password"), bool
    )  # Ensure it returns a boolean and not the actual hashed password
    assert user_data["hashed_password"] is True


def test_read_user_me_unauthenticated(client: TestClient) -> None:
    """
    Test retrieving user /me without authentication.
    """
    response = client.get(
        "/users/me",
        # No headers
    )
    assert response.status_code == 401


# ===========================
# 3. Delete User (/me) Endpoint
# ===========================


def test_delete_user_me_success(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test successful deletion of the current (normal) user.
    """
    user_email = settings.EMAIL_TEST_USER
    # Verify user exists before deletion
    user_before = get_user_by_email(db, user_email)
    assert user_before is not None

    response = client.delete(
        "/users/me",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["msg"] == "User deleted successfully"

    # Verify user is deleted from DB
    user_after = get_user_by_email(db, user_email)
    assert user_after is None

    # Verify token is now invalid (user not found or inactive)
    response_get = client.get(
        "/users/me",
        headers=normal_user_token_headers,
    )
    assert response_get.status_code == 404
    response_get_data = response_get.json()
    assert response_get_data["detail"] == "User not found"


def test_delete_user_me_superuser_forbidden(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test that a superuser cannot delete themselves via the /me endpoint.
    """
    response = client.delete(
        "/users/me",
        headers=superuser_token_headers,
    )
    assert response.status_code == 403
    assert "Super users are not allowed" in response.json()["detail"]

    # Verify superuser still exists
    superuser = get_user_by_email(db, settings.EMAIL_TEST_USER)
    assert superuser is not None
    assert superuser.is_superuser is True


def test_delete_user_me_unauthenticated(client: TestClient) -> None:
    """
    Test deleting user /me without authentication.
    """
    response = client.delete(
        "/users/me",
        # No headers
    )
    assert response.status_code == 401


# ===========================
# 4. Get User by ID Endpoint (Superuser)
# ===========================


def test_read_user_by_id_success(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test successful retrieval of a specific user by ID by a superuser.
    """
    user_to_get = create_user(db, password=None)  # Create a random user
    assert user_to_get.id is not None

    response = client.get(
        f"/users/{user_to_get.id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["id"] == str(user_to_get.id)
    assert user_data["email"] == user_to_get.email
    assert isinstance(
        user_data.get("hashed_password"), bool
    )  # Ensure it returns a boolean and not the actual hashed password
    assert user_data["hashed_password"] is False


def test_read_user_by_id_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test retrieving a user by a non-existent ID by a superuser.
    """
    non_existent_id = uuid4()
    response = client.get(
        f"/users/{non_existent_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404


def test_read_user_by_id_normal_user_forbidden(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test that a normal user cannot retrieve another user by ID.
    """
    user_to_get = create_user(db)  # Create a random user
    assert user_to_get.id is not None

    response = client.get(
        f"/users/{user_to_get.id}",
        headers=normal_user_token_headers,  # Use normal user token
    )
    assert response.status_code == 403  # Expect Forbidden


def test_read_user_by_id_unauthenticated(client: TestClient, db: Session) -> None:
    """
    Test retrieving a user by ID without authentication.
    """
    user_to_get = create_user(db)  # Need an ID, so create a user
    assert user_to_get.id is not None

    response = client.get(
        f"/users/{user_to_get.id}",
        # No headers
    )
    assert response.status_code == 401  # Expect Unauthorized


# ===========================
# 5. Update User by ID Endpoint (Superuser)
# ===========================


def test_update_user_by_id_success(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test successful update of a user by ID by a superuser.
    """
    user_to_update = create_user(db)
    assert user_to_update.id is not None
    original_email = user_to_update.email

    new_full_name = random_lower_string()
    new_email = random_email()
    update_data = {
        "full_name": new_full_name,
        "role": "editor",
        "email": new_email,
        "password": "newpassword",
        # Can also include is_active, is_superuser here if needed
    }

    response = client.post(  # Note: API route uses POST for update by ID
        f"/users/{user_to_update.id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200
    updated_user_data = response.json()
    assert updated_user_data["id"] == str(user_to_update.id)
    assert updated_user_data["email"] == new_email
    assert updated_user_data["full_name"] == new_full_name
    assert updated_user_data["role"] == "editor"

    # Verify DB changes
    db.expire_all()
    db_user = db.get(fast_auth.User, user_to_update.id)  # Fetch by primary key
    assert db_user is not None
    assert db_user.email == new_email
    assert db_user.full_name == new_full_name
    verify_password(
        plain_password="newpassword", hashed_password=db_user.hashed_password
    )
    assert db_user.role == "editor"

    # Verify old email is gone
    assert get_user_by_email(db, original_email) is None


def test_update_user_by_id_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test updating a non-existent user ID by a superuser.
    """
    non_existent_id = uuid4()
    update_data = {"full_name": "Any Name"}
    response = client.post(
        f"/users/{non_existent_id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_update_user_by_id_email_conflict(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test updating a user's email to one already taken by another user (via superuser).
    """
    user_to_update = create_user(db, email=random_email())
    other_user = create_user(db, email=random_email())  # The email we want to use
    assert user_to_update.id is not None

    update_data = {
        "email": other_user.email,  # Try to use the other user's email
    }
    response = client.post(
        f"/users/{user_to_update.id}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 409
    assert "username is not available" in response.json()["detail"]


def test_update_user_by_id_normal_user_forbidden(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test that a normal user cannot update another user by ID.
    """
    user_to_update = create_user(db)
    assert user_to_update.id is not None
    update_data = {"full_name": "Any Name"}

    response = client.post(
        f"/users/{user_to_update.id}",
        headers=normal_user_token_headers,  # Use normal user token
        json=update_data,
    )
    assert response.status_code == 403  # Expect Forbidden


def test_update_user_by_id_unauthenticated(client: TestClient, db: Session) -> None:
    """
    Test updating a user by ID without authentication.
    """
    user_to_update = create_user(db)
    assert user_to_update.id is not None
    update_data = {"full_name": "Any Name"}

    response = client.post(
        f"/users/{user_to_update.id}",
        json=update_data,  # No headers
    )
    assert response.status_code == 401  # Expect Unauthorized


# ===========================
# 6. Delete User by ID Endpoint (Superuser)
# ===========================


def test_delete_user_by_id_success(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test successful deletion of a user by ID by a superuser.
    """
    user_to_delete = create_user(db)
    assert user_to_delete.id is not None
    user_id = user_to_delete.id

    # Verify user exists before deletion
    user_before = db.get(fast_auth.User, user_id)
    assert user_before is not None

    response = client.delete(
        f"/users/{user_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    assert response.json()["msg"] == "User deleted successfully."

    # Verify user is deleted from DB
    db.expire_all()
    user_after = db.get(fast_auth.User, user_id)
    assert user_after is None


def test_delete_user_by_id_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test deleting a non-existent user ID by a superuser.
    """
    non_existent_id = uuid4()
    response = client.delete(
        f"/users/{non_existent_id}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_delete_user_by_id_normal_user_forbidden(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test that a normal user cannot delete another user by ID.
    """
    user_to_delete = create_user(db)
    assert user_to_delete.id is not None

    response = client.delete(
        f"/users/{user_to_delete.id}",
        headers=normal_user_token_headers,  # Use normal user token
    )
    assert response.status_code == 403  # Expect Forbidden


def test_delete_user_by_id_unauthenticated(client: TestClient, db: Session) -> None:
    """
    Test deleting a user by ID without authentication.
    """
    user_to_delete = create_user(db)
    assert user_to_delete.id is not None

    response = client.delete(
        f"/users/{user_to_delete.id}",
        # No headers
    )
    assert response.status_code == 401  # Expect Unauthorized


# ===========================
# 7. Get All Users Endpoint (Superuser)
# ===========================


def test_read_all_users_success(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test successful retrieval of all users by a superuser.
    """
    # Create a couple of users to ensure the list isn't empty
    user1 = create_user(db, email=random_email())
    user2 = create_user(db, email=random_email())
    # The superuser itself also exists from the fixture setup
    initial_user_count = 3  # user1, user2, superuser

    response = client.get(
        "/users/",
        headers=superuser_token_headers,
    )
    assert response.status_code == 200
    users_data = response.json()
    assert isinstance(users_data, list)
    # Check if the count matches (assuming default page size is large enough)
    # This might need adjustment if default page size is small or many users exist
    assert len(users_data) >= initial_user_count

    # Verify structure of one user in the list
    found_user1 = any(u["id"] == str(user1.id) for u in users_data)
    found_user2 = any(u["id"] == str(user2.id) for u in users_data)
    assert found_user1
    assert found_user2
    assert isinstance(
        users_data[0].get("hashed_password"), bool
    )  # Ensure it returns a boolean and not the actual hashed password


def test_read_all_users_pagination(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test pagination works for retrieving all users.
    """
    # Create more users than one page
    total_users_to_create = settings.MULTI_MAX + 3
    created_emails = {
        settings.EMAIL_TEST_USER,
        settings.FIRST_SUPERUSER,
    }  # Include superuser
    for _ in range(total_users_to_create - 1):  # -1 because superuser exists
        user = create_user(db, email=random_email())
        created_emails.add(user.email)

    # Get first page (page=0)
    response_p0 = client.get(
        "/users/?page=0",
        headers=superuser_token_headers,
    )
    assert response_p0.status_code == 200
    users_p0 = response_p0.json()
    assert isinstance(users_p0, list)
    assert len(users_p0) == settings.MULTI_MAX
    emails_p0 = {u["email"] for u in users_p0}

    # Get second page (page=1)
    response_p1 = client.get(
        "/users/?page=1",
        headers=superuser_token_headers,
    )
    assert response_p1.status_code == 200
    users_p1 = response_p1.json()
    assert isinstance(users_p1, list)
    assert (
        len(users_p1) - 1 == total_users_to_create - settings.MULTI_MAX
    )  # Should be 3 users plus superuser
    emails_p1 = {u["email"] for u in users_p1}

    # Ensure pages are distinct and contain all created users
    assert emails_p0.isdisjoint(emails_p1)
    combined_emails = emails_p0.union(emails_p1)
    assert combined_emails == created_emails


def test_read_all_users_normal_user_forbidden(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test that a normal user cannot retrieve all users.
    """
    response = client.get(
        "/users/",
        headers=normal_user_token_headers,  # Use normal user token
    )
    assert response.status_code == 403  # Expect Forbidden


def test_read_all_users_unauthenticated(client: TestClient) -> None:
    """
    Test retrieving all users without authentication.
    """
    response = client.get(
        "/users/",
        # No headers
    )
    assert response.status_code == 401  # Expect Unauthorized


def test_admin_endpoints_access_control(client: TestClient, db: Session) -> None:
    """
    Test RBAC on an endpoint protected by `require_role(['admin'])`.
    - Superuser: should pass.
    - User with 'admin' role: should pass.
    - User with 'user' role: should fail.
    - Unauthenticated: should fail.
    """
    # Create different users
    superuser_email = random_email()
    admin_user_email = random_email()
    normal_user_email = random_email()
    test_password = "password123"

    create_user(db, email=superuser_email, password=test_password, is_superuser=True)
    create_user(
        db,
        email=admin_user_email,
        password=test_password,
        is_superuser=False,
        role="admin",
    )
    create_user(
        db,
        email=normal_user_email,
        password=test_password,
        is_superuser=False,
        role="user",
    )

    # Get tokens
    superuser_headers = user_authentication_headers(
        client=client, email=superuser_email, password=test_password
    )
    admin_headers = user_authentication_headers(
        client=client, email=admin_user_email, password=test_password
    )
    normal_user_headers = user_authentication_headers(
        client=client, email=normal_user_email, password=test_password
    )

    # Test multiple admin-only endpoints
    admin_endpoints = ["/users/", f"/users/{create_user(db).id}"]
    for endpoint in admin_endpoints:
        # 1. Superuser should pass
        response_su = client.get(endpoint, headers=superuser_headers)
        assert response_su.status_code == 200

        # 2. Admin (non-superuser) should pass
        response_admin = client.get(endpoint, headers=admin_headers)
        assert response_admin.status_code == 200

        # 3. Normal user should fail
        response_user = client.get(endpoint, headers=normal_user_headers)
        assert response_user.status_code == 403
        assert "required permissions" in response_user.json()["detail"]

        # 4. Unauthenticated should fail
        response_unauth = client.get(endpoint)
        assert response_unauth.status_code == 401


# ===========================
# 8. Toggle User State Endpoint (Superuser)
# ===========================


def test_toggle_user_state_activate(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test activating an inactive user by a superuser.
    """
    # Create an inactive user
    inactive_user = create_user(db, is_active=False)
    assert inactive_user.id is not None
    assert not inactive_user.is_active

    toggle_data = {
        "user_email": inactive_user.email,
    }

    response = client.post(
        "/users/toggle-state",
        headers=superuser_token_headers,
        json=toggle_data,
    )
    assert response.status_code == 200
    assert response.json()["msg"] == "User state toggled successfully."

    # Verify user is now active in DB
    db.refresh(inactive_user)  # Refresh object state from DB
    assert inactive_user.is_active


def test_toggle_user_state_deactivate(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test deactivating an active user by a superuser.
    """
    # Create an active user
    active_user = create_user(db, is_active=True)
    assert active_user.id is not None
    assert active_user.is_active

    toggle_data = {
        "user_email": active_user.email,
    }

    response = client.post(
        "/users/toggle-state",
        headers=superuser_token_headers,
        json=toggle_data,
    )
    assert response.status_code == 200
    assert response.json()["msg"] == "User state toggled successfully."

    # Verify user is now inactive in DB
    db.refresh(active_user)
    assert not active_user.is_active


# Note: The route's check `if not response:` implies the CRUD function returns a
# truthy value on success and falsy on failure (e.g., user not found).
def test_toggle_user_state_user_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test toggling state for a non-existent user email.
    """
    non_existent_email = random_email()
    toggle_data = {"user_email": non_existent_email}
    response = client.post(
        "/users/toggle-state",
        headers=superuser_token_headers,
        json=toggle_data,
    )
    # Based on route logic `if not response: raise HTTPException(400...`
    assert response.status_code == 400
    assert "Invalid request" in response.json()["detail"]


def test_toggle_user_state_normal_user_forbidden(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test that a normal user cannot toggle user state.
    """
    user_to_toggle = create_user(db)
    toggle_data = {
        "email": user_to_toggle.email,
        "is_active": not user_to_toggle.is_active,
    }

    response = client.post(
        "/users/toggle-state",
        headers=normal_user_token_headers,  # Use normal user token
        json=toggle_data,
    )
    assert response.status_code == 403  # Expect Forbidden


def test_toggle_user_state_unauthenticated(client: TestClient, db: Session) -> None:
    """
    Test toggling user state without authentication.
    """
    user_to_toggle = create_user(db)
    toggle_data = {
        "email": user_to_toggle.email,
        "is_active": not user_to_toggle.is_active,
    }

    response = client.post(
        "/users/toggle-state",
        json=toggle_data,  # No headers
    )
    assert response.status_code == 401  # Expect Unauthorized


# ===========================
# 9. Create User Endpoint (Superuser)
# ===========================


def test_create_user_success(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """
    Test successful creation of a new user by a superuser.
    """
    email = random_email()
    password = random_lower_string()
    full_name = random_lower_string(8)
    user_data = {
        "email": email,
        "password": password,
        "full_name": full_name,
        "is_active": True,
        "is_superuser": False,
        "language": "en",
    }

    response = client.post(
        "/users/create",
        headers=superuser_token_headers,
        json=user_data,
    )
    assert response.status_code == 200
    created_user = response.json()
    assert created_user["email"] == email
    assert created_user["full_name"] == full_name
    assert created_user["is_active"] is True
    assert created_user["is_superuser"] is False
    assert created_user["role"] == "user"
    assert "id" in created_user
    assert isinstance(
        created_user.get("hashed_password"), bool
    )  # Ensure it returns a boolean and not the actual hashed password
    assert "language" in created_user
    assert created_user["language"] == "en"

    # Verify user exists in DB
    db_user = get_user_by_email(db, email)
    assert db_user is not None
    assert db_user.email == email
    assert db_user.full_name == full_name
    assert db_user.role == "user"


def test_create_user_existing_email(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test creating a user with an email that already exists.
    """
    existing_email = settings.EMAIL_TEST_USER  # Use the superuser's email
    password = random_lower_string()
    user_data = {"email": existing_email, "password": password}

    response = client.post(
        "/users/create",
        headers=superuser_token_headers,
        json=user_data,
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


def test_create_user_invalid_data(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """
    Test creating a user with invalid data (e.g., missing required fields).
    """
    # Missing email
    user_data_no_email = {"password": random_lower_string()}
    response = client.post(
        "/users/create",
        headers=superuser_token_headers,
        json=user_data_no_email,
    )
    assert response.status_code == 422

    # Invalid email format
    user_data_bad_email = {"email": "not-an-email", "password": random_lower_string()}
    response = client.post(
        "/users/create",
        headers=superuser_token_headers,
        json=user_data_bad_email,
    )
    assert response.status_code == 422


def test_create_user_normal_user_forbidden(
    client: TestClient, normal_user_token_headers: dict[str, str]
) -> None:
    """
    Test that a normal user cannot create a new user.
    """
    user_data = {
        "email": random_email(),
        "password": random_lower_string(),
    }
    response = client.post(
        "/users/create",
        headers=normal_user_token_headers,  # Use normal user token
        json=user_data,
    )
    assert response.status_code == 403  # Expect Forbidden


def test_create_user_unauthenticated(client: TestClient) -> None:
    """
    Test creating a user without authentication.
    """
    user_data = {
        "email": random_email(),
        "password": random_lower_string(),
    }
    response = client.post(
        "/users/create",
        json=user_data,  # No headers
    )
    assert response.status_code == 401  # Expect Unauthorized
