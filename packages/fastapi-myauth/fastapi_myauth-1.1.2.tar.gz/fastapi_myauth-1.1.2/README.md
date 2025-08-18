# FastAPI MyAuth

[![PyPI version](https://badge.fury.io/py/fastapi_myauth.svg)](https://badge.fury.io/py/fastapi_myauth)
[![Python Version](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.svg)](https://github.com/astral-sh/ruff)
[![codecov](https://codecov.io/gh/<YOUR_GITHUB_USERNAME>/fastapi-myauth/branch/main/graph/badge.svg?token=<YOUR_CODECOV_TOKEN_IF_PRIVATE_REPO>)](https://codecov.io/gh/<YOUR_GITHUB_USERNAME>/fastapi-myauth) <!-- Replace <YOUR_GITHUB_USERNAME> and provide a token if private, otherwise remove token -->

A flexible and secure authentication library for FastAPI, designed to integrate seamlessly with your existing SQLModel ORM. `FastAPI MyAuth` provides robust features including:

- **User Management**: CRUD operations for users, including activation/deactivation.
- **Authentication Methods**:
  - Traditional email/password login.
  - Magic link based login for a passwordless experience.
  - Refresh token mechanism for extended sessions without re-authenticating.
- **Security Features**:
  - Password hashing with Argon2.
  - JSON Web Token (JWT) based authentication.
  - Two-Factor Authentication (TOTP) support.
  - Password recovery flows.
- **Email Integration**: Templates and functions for sending various authentication-related emails (e.g., password reset, magic links).
- **Role-Based Access Control (RBAC)**: Easily add roles to users and protect endpoints based on these roles.
- **Extensible**: Designed with generics to allow customization of the `User` model and integration with existing database sessions.

## 🚀 Getting Started

To quickly integrate `FastAPI MyAuth` into your FastAPI application, install it via pip:

```bash
pip install fastapi_myauth
```

Then, you can typically set up the authentication router in your FastAPI application like this:

```python
from fastapi import FastAPI
from sqlmodel import Session, create_engine, SQLModel

from fastapi_myauth import models
from fastapi_myauth.auth import FastAuth
from fastapi_myauth.config import settings

app = FastAPI()

# Your database engine setup (example for SQLite)
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency to get a database session
def get_db():
    with Session(engine) as session:
        yield session

# Initialize FastAuth with your custom User model (or use default)
# You can extend models.User, models.UserCreate, models.UserRead, models.UserUpdate
# to add custom fields. For example, if you want a `language` field:
class MyUser(models.User, table=True): # Important: table=True on your concrete user model
    language: str = "en"

class MyUserRead(models.UserRead):
    language: str

class MyUserCreate(models.UserCreate):
    language: str | None = None

class MyUserUpdate(models.UserUpdate):
    language: str | None = None


fast_auth = FastAuth(
    get_db=get_db,
    user_model=MyUser,
    user_read=MyUserRead,
    user_create=MyUserCreate,
    user_update=MyUserUpdate,
)

# Call this once your app starts, e.g., in a startup event or directly
create_db_and_tables()

# Include the authentication router
app.include_router(fast_auth.get_router())

@app.on_event("startup")
def on_startup():
    # Initialize the first superuser if not exists
    with Session(engine) as session:
        crud_user = fast_auth.crud_user()
        user = crud_user.get_by_email(session, email=settings.FIRST_SUPERUSER)
        if not user:
            user_in = MyUserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                language="en" # Set default for custom field
            )
            crud_user.create(session, obj_in=user_in)

# Example protected endpoint
from fastapi import Depends
from fastapi_myauth.api.deps import APIDependencies

# Get dependency instance from your fast_auth object
deps_instance = fast_auth.deps()

@app.get("/protected-route")
def read_protected_route(
    current_user: MyUserRead = Depends(deps_instance.get_current_active_user)
):
    return {"message": f"Hello, {current_user.email}! This is a protected route."}

```

For more detailed usage instructions, configuration options, and advanced customization, please refer to the [Usage Documentation](docs/usage/GETTING_STARTED.md).

## 🌳 Project Structure

```
fastapi_myauth/
├── api/                  # FastAPI routers and dependencies for REST API endpoints
│   ├── v1/               # Versioned API endpoints (e.g., login, users)
│   └── deps.py           # FastAPI dependency injection for auth components
├── crud/                 # CRUD operations for database models
│   ├── base.py           # Generic CRUD base class
│   ├── crud_token.py     # CRUD for refresh tokens
│   └── crud_user.py      # CRUD for user operations
├── email/                # Email sending utilities and templates
├── models/               # Pydantic/SQLModel definitions for data structures
├── security.py           # Password hashing, JWT handling, TOTP
├── config.py             # Application settings
├── auth.py               # Main FastAuth class for setup and router inclusion
└── test_main.py          # Example FastAPI app for testing and demonstration
```

## 📚 Documentation

Detailed documentation is available in the `docs` directory:

- **[Usage Documentation](docs/usage/GETTING_STARTED.md)**: Learn how to install, configure, and use the `fastapi_myauth` library in your projects.
- **[Development & Contributing](docs/development/CONTRIBUTING.md)**: Information for developers interested in contributing to the project, including setup instructions and coding standards.

## ✨ Features at a Glance

- **FastAPI Integration**: Designed exclusively for FastAPI.
- **SQLModel Native**: Works seamlessly with SQLModel for ORM operations.
- **Secure Authentication**: Built with modern security practices (Argon2 for passwords, JWTs).
- **Email Management**: Integrated email sending for common auth flows.
- **Customizable User Model**: Easily extendable `User` model to fit specific application needs.
- **Dependency Injection**: Leverages FastAPI's dependency injection system for robust and testable code.

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](docs/development/CONTRIBUTING.md) for details on how to get started.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
