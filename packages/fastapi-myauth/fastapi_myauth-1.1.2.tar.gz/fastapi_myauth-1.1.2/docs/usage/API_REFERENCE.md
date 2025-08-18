# 📚 API Reference for FastAPI MyAuth

This document provides an overview of the REST API endpoints exposed by `FastAPI MyAuth`. When you include `fast_auth.get_router()` in your FastAPI application, these endpoints become available. The common prefix is usually `/auth` if you include it as `app.include_router(fast_auth.get_router(), prefix="/auth")`.

For full details, including request/response schemas, refer to your application's Swagger UI (`/docs`) or OpenAPI specification (`/openapi.json`).

## 🔑 Login & Authentication Endpoints (`/auth/login`)

These endpoints handle user authentication and token management.

- **POST `/auth/login/signup`**

  - **Description**: Registers a new user account.
  - **Permissions**: Open access (controlled by `USERS_OPEN_REGISTRATION` setting).
  - **Request Body**:
    ```json
    {
      "email": "user@example.com",
      "password": "strongPassword123",
      "full_name": "Optional Name"
    }
    ```
  - **Response**: `UserRead` model of the newly created user.

- **POST `/auth/login/oauth`**

  - **Description**: Standard OAuth2 token endpoint for email and password authentication. Returns a JWT access token and a refresh token.
  - **Permissions**: Open access.
  - **Request Body**: Form-data with `username` (email) and `password`.
    ```
    username: user@example.com
    password: strongPassword123
    ```
  - **Response**: `Token` model (containing `access_token`, `refresh_token`, `token_type`). If 2FA (TOTP) is enabled for the user, only a TOTP-purpose access token is returned (the `refresh_token` will be null), and the client must then proceed to `POST /auth/login/totp`.

- **POST `/auth/login/magic/{email}`**

  - **Description**: Initiates a passwordless login flow by sending a magic link to the user's email.
  - **Permissions**: Open access. Will create a user if `USERS_OPEN_REGISTRATION` is `True` and the email doesn't exist.
  - **Path Parameter**: `email` (string).
  - **Response**: `WebToken` model (containing a `claim` token for client-side processing).

- **POST `/auth/login/claim`**

  - **Description**: Completes the magic link login flow. Requires the email-sent token in the `Authorization` header and the client-side `claim` token in the request body.
  - **Permissions**: Requires valid magic link tokens.
  - **Request Body**:
    ```json
    {
      "claim": "client_claim_token"
    }
    ```
  - **Response**: `Token` model (containing `access_token`, `refresh_token`, `token_type`).

- **POST `/auth/login/refresh`**

  - **Description**: Exchanges a valid refresh token for a new access token and a new refresh token. The provided refresh token is immediately revoked upon use.
  - **Permissions**: Requires a valid refresh token in the `Authorization` header.
  - **Response**: `Token` model.

- **POST `/auth/login/revoke`**

  - **Description**: Revokes the provided refresh token, invalidating it.
  - **Permissions**: Requires a valid refresh token in the `Authorization` header.
  - **Response**: `Msg` model (`{"msg": "Token revoked successfully."}`).

- **POST `/auth/login/recover/{email}`**

  - **Description**: Initiates the password recovery process by sending a password reset link to the user's email.
  - **Permissions**: Open access.
  - **Path Parameter**: `email` (string).
  - **Response**: `WebToken` model if email succeeds, or `Msg` (generic success message to prevent user enumeration).

- **POST `/auth/login/reset`**
  - **Description**: Resets the user's password using the tokens received from the password recovery email.
  - **Permissions**: Requires valid password reset tokens in the `Authorization` header (email token) and request body (client claim token).
  - **Request Body**:
    ```json
    {
      "new_password": "newStrongPassword123",
      "claim": "reset_claim_token"
    }
    ```
  - **Response**: `Msg` model (`{"msg": "Password updated successfully."}`).

## 🔐 Two-Factor Authentication (TOTP) Endpoints (`/auth/login`)

- **POST `/auth/login/new-totp`**

  - **Description**: Generates new TOTP (Time-based One-Time Password) secret keys (e.g., for Google Authenticator) for the authenticated user. **Does not enable TOTP yet.**
  - **Permissions**: Requires an authenticated, active user (`get_current_active_user`).
  - **Response**: `NewTOTPResponse` model (contains `key` for display and `uri` for QR code generation).

- **POST `/auth/login/totp`**

  - **Description**: Finalizes login for users with TOTP enabled. Requires a valid TOTP code in the request body. Only callable with a special access token generated during `oauth` or `magic/claim` login that specifies `totp: true`.
  - **Permissions**: Requires an authenticated user with a `totp: true` token (`get_totp_user`).
  - **Request Body**:
    ```json
    {
      "claim": "123456" # The 6-digit TOTP code
    }
    ```
  - **Response**: `Token` model (new `access_token` and `refresh_token` for full access).

- **PUT `/auth/login/totp`**

  - **Description**: Enables TOTP for the authenticated user's account. Requires the TOTP secret generated by `/login/new-totp` and a verification code. Optionally requires the user's current password if one is set.
  - **Permissions**: Requires an authenticated, active user.
  - **Request Body**:
    ```json
    {
      "claim": "123456", # The 6-digit TOTP code
      "uri": "otpauth://...", # The URI generated by new-totp
      "password": "currentPassword" # Optional, if user has a password set
    }
    ```
  - **Response**: `Msg` model (`{"msg": "TOTP enabled. Do not lose your recovery code."}`).

- **DELETE `/auth/login/totp`**
  - **Description**: Disables TOTP for the authenticated user's account. Optionally requires the user's current password if one is set.
  - **Permissions**: Requires an authenticated, active user.
  - **Request Body**:
    ```json
    {
      "original": "currentPassword" # Optional, if user has a password set
    }
    ```
  - **Response**: `Msg` model (`{"msg": "TOTP disabled. You can re-enable it at any time."}`).

## 👤 User Management Endpoints (`/auth/users`)

These endpoints allow users to manage their own profiles and administrators to manage other users.

- **PUT `/auth/users/me`**

  - **Description**: Updates the current authenticated user's profile information (email, full name, password). Requires the `original` password if a password exists and other sensitive fields are updated.
  - **Permissions**: Requires an authenticated, active user (`get_current_active_user`).
  - **Request Body**: `UserUpdate` model (e.g., `{"full_name": "Jane Doe", "email": "new@example.com", "password": "newPassword", "original": "currentPassword"}`).
  - **Response**: `UserRead` model of the updated user.

- **GET `/auth/users/me`**

  - **Description**: Retrieves the current authenticated user's profile details.
  - **Permissions**: Requires an authenticated, active user.
  - **Response**: `UserRead` model of the current user.

- **DELETE `/auth/users/me`**

  - **Description**: Deletes the current authenticated user's account. Superusers are prevented from deleting themselves.
  - **Permissions**: Requires an authenticated, active user.
  - **Response**: `Msg` model (`{"msg": "User deleted successfully"}`).

- **GET `/auth/users/`**

  - **Description**: Retrieves a list of all users in the system. Supports pagination using `page` query parameter.
  - **Permissions**: Requires user with `admin` role or superuser.
  - **Query Parameters**: `page` (int, default: 0).
  - **Response**: List of `UserRead` models.

- **POST `/auth/users/toggle-state`**

  - **Description**: Toggles the active status (`is_active`) of a user by their email.
  - **Permissions**: Requires user with `admin` role or superuser.
  - **Request Body**:
    ```json
    {
      "user_email": "target_user@example.com"
    }
    ```
  - **Response**: `Msg` model (`{"msg": "User state toggled successfully."}`).

- **POST `/auth/users/create`**

  - **Description**: Creates a new user account by an administrator.
  - **Permissions**: Requires user with `admin` role or superuser.
  - **Request Body**: `UserCreate` model (e.g., `{"email": "newuser@example.com", "password": "tempPassword", "is_superuser": false}`.
  - **Response**: `UserRead` model of the created user.

- **GET `/auth/users/{user_id}`**

  - **Description**: Retrieves a specific user's details by their UUID.
  - **Permissions**: Requires user with `admin` role or superuser.
  - **Path Parameter**: `user_id` (UUID).
  - **Response**: `UserRead` model of the requested user.

- **POST `/auth/users/{user_id}`**

  - **Description**: Updates a specific user's profile information by their UUID.
  - **Permissions**: Requires user with `admin` role or superuser.
  - **Path Parameter**: `user_id` (UUID).
  - **Request Body**: `UserUpdate` model.
  - **Response**: `UserRead` model of the updated user.

- **DELETE `/auth/users/{user_id}`**
  - **Description**: Deletes a specific user's account by their UUID.
  - **Permissions**: Requires user with `admin` role or superuser.
  - **Path Parameter**: `user_id` (UUID).
  - **Response**: `Msg` model (`{"msg": "User deleted successfully."}`).

This overview should provide a solid foundation for understanding and interacting with the `FastAPI MyAuth` API. Remember to consult the live `/docs` endpoint of your running application for the most up-to-date and exact schema definitions.
