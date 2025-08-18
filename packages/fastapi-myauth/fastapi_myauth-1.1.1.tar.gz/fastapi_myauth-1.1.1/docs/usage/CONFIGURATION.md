# ⚙️ Configuration for FastAPI MyAuth

`FastAPI MyAuth` uses a `Settings` class (powered by `pydantic-settings`) to manage its configuration. These settings can be loaded from environment variables, `.env` files, or directly provided in your code.

You can import and inspect the default settings:

```python
from fastapi_myauth.config import settings

print(settings.PROJECT_NAME)
print(settings.SECRET_KEY)
```

## 🌍 How to Configure

`pydantic-settings` prioritizes settings in the following order (from lowest to highest priority):

1.  Default values in the `Settings` class.
2.  Environment variables (e.g., `SECRET_KEY=your_secret_key`).
3.  `.env` file (e.g., in your project root, `SECRET_KEY="your-secret-key"`).

### Example `.env` file:

Create a file named `.env` in the root of your project:

```dotenv
# .env examples
PROJECT_NAME="My Awesome App"
SECRET_KEY="a_very_long_and_random_string_of_characters_for_jwt_signing"
TOTP_SECRET_KEY="another_very_long_and_random_string_for_totp_secrets" # Should be different from SECRET_KEY

# Token Expiry (in seconds)
ACCESS_TOKEN_EXPIRE_SECONDS=1800 # 30 minutes
REFRESH_TOKEN_EXPIRE_SECONDS=2592000 # 30 days

# Frontend URL (used for email links like password reset)
FRONTEND_URL="http://localhost:3000"
FRONTEND_HOST="localhost:3000" # Or your domain, e.g., 'your-app-frontend.com'
SERVER_BOT="MyAuthBot" # Name displayed in email footers

# Email Settings (for password resets, magic links, new account notifications)
# Set EMAILS_ENABLED to true if SMTP_HOST, SMTP_PORT, and EMAILS_FROM_EMAIL are set
SMTP_TLS=True
SMTP_PORT=587
SMTP_HOST="smtp.mailtrap.io" # Example for development
SMTP_USER="your_smtp_user"
SMTP_PASSWORD="your_smtp_password"
EMAILS_FROM_EMAIL="noreply@yourapp.com"
EMAILS_FROM_NAME="Your App Support"
EMAIL_TEMPLATES_DIR="/app/email_templates/build" # Path to your built email templates

# User Registration Settings
USERS_OPEN_REGISTRATION=True # Allow users to sign up without admin intervention

# Initial Superuser (used by the startup script in the example)
FIRST_SUPERUSER="admin@example.com"
FIRST_SUPERUSER_PASSWORD="ChangeMeInProduction!" # Change this for production!
```

## 🔑 Key Configuration Options

Here's a breakdown of the most important settings available in `fastapi_myauth.config.Settings`:

- **`SECRET_KEY` (str)**:
  - **Purpose**: Used for signing JWTs (JSON Web Tokens). **Crucial for security.**
  - **Recommendations**: Must be a long, random string. Generate with `secrets.token_urlsafe(32)` or similar. **Do not hardcode in production.**
- **`TOTP_SECRET_KEY` (str)**:
  - **Purpose**: Used for generating TOTP secrets for 2FA. **Crucial for security.**
  - **Recommendations**: Must be a long, random string, different from `SECRET_KEY`.
- **`ACCESS_TOKEN_EXPIRE_SECONDS` (int)**:
  - **Purpose**: How long (in seconds) an access token is valid.
  - **Default**: 1800 (30 minutes).
  - **Recommendations**: Keep it short (e.g., 5-30 minutes). Refreshed using `REFRESH_TOKEN_EXPIRE_SECONDS`.
- **`REFRESH_TOKEN_EXPIRE_SECONDS` (int)**:
  - **Purpose**: How long (in seconds) a refresh token is valid.
  - **Default**: 2592000 (30 days).
  - **Recommendations**: Longer than access tokens. Allows users to stay logged in without re-entering credentials.
- **`JWT_ALGO` (str)**:
  - **Purpose**: The JWT signing algorithm to use.
  - **Default**: "HS512".
  - **Recommendations**: "HS256" or "HS512" are common symmetric algorithms.
- **`TOTP_ALGO` (Literal["sha1", "sha256", "sha512"])**:
  - **Purpose**: The hashing algorithm for TOTP.
  - **Default**: "sha1".
  - **Recommendations**: SHA1 is standard for TOTP, but can be changed.
- **`FRONTEND_HOST` (str)**:
  - **Purpose**: The hostname of your frontend application. Used for display in emails.
  - **Default**: "localhost".
- **`FRONTEND_URL` (AnyHttpUrl)**:
  - **Purpose**: The base URL of your frontend application. Used for constructing active links in emails (e.g., password reset, magic links).
  - **Default**: "http://localhost:3000".
- **`SERVER_BOT` (str)**:
  - **Purpose**: Name of the bot/server sending emails. Displayed in email footers.
  - **Default**: "Symona".
- **`PROJECT_NAME` (str)**:
  - **Purpose**: The name of your project. Used in email subjects and bodies.
  - **Default**: "FastAPI Auth".
- **`MULTI_MAX` (int)**:
  - **Purpose**: Maximum number of items returned in a page for CRUD operations (e.g., `GET /users/`).
  - **Default**: 20.
- **Email Settings (`SMTP_TLS`, `SMTP_PORT`, `SMTP_HOST`, `SMTP_USER`, `SMTP_PASSWORD`, `EMAILS_FROM_EMAIL`, `EMAILS_FROM_NAME`)**:
  - **Purpose**: Credentials and configuration for sending emails.
  - **`EMAILS_ENABLED`**: Automatically set to `True` if `SMTP_HOST`, `SMTP_PORT`, and `EMAILS_FROM_EMAIL` are provided.
- **`EMAIL_RESET_TOKEN_EXPIRE_HOURS` (int)**:
  - **Purpose**: How long (in hours) a password reset token is valid.
  - **Default**: 48.
- **`EMAIL_TEMPLATES_DIR` (str)**:
  - **Purpose**: Path to the directory where your compiled email templates (`.html` files) are located.
  - **Default**: "/app/app/email-templates/build".
  - **Note**: Make sure to adjust this path if your templates are located elsewhere in your deployment.
- **`USERS_OPEN_REGISTRATION` (bool)**:
  - **Purpose**: If `True`, allows new users to sign up via the `/login/signup` endpoint without explicit administrator creation.
  - **Default**: `True`.
- **`FIRST_SUPERUSER` (EmailStr)**:
  - **Purpose**: Default email for the first superuser created on application startup (if `on_startup` hook is used).
  - **Default**: "admin@admin.com".
- **`FIRST_SUPERUSER_PASSWORD` (str)**:
  - **Purpose**: Default password for the first superuser created. **Change immediately in production.**
  - **Default**: "12345678".
- **`EMAIL_TEST_USER` (EmailStr)**:
  - **Purpose**: A dedicated email for testing purposes.
  - **Default**: "test@example.com".

By appropriately setting these variables, you can tailor `FastAPI MyAuth` to your application's specific requirements.
