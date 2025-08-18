# 🚀 Getting Started with FastAPI MyAuth

This guide will walk you through the basic steps to integrate `FastAPI MyAuth` into your FastAPI application.

## 📦 Installation

First, install `fastapi_myauth` using pip:

```bash
pip install fastapi_myauth
```

This will also install its core dependencies, including FastAPI, SQLModel, Passlib, and others.

## 👩‍💻 Basic Usage Example

Let's integrate `FastAPI MyAuth` into a simple FastAPI application.

### 1. Define your Database Setup

`FastAPI MyAuth` is designed to be database-agnostic, using SQLModel for ORM. You need to provide your database engine and a dependency function to get a database session.

Create `main.py`:

```python
# main.py
from fastapi import FastAPI
from sqlmodel import Session, create_engine, SQLModel
from fastapi_myauth.auth import FastAuth
from fastapi_myauth.config import settings
from fastapi_myauth import models # Import default models if not customizing

app = FastAPI(title="My Auth App")

# --- Database Setup ---
# For demonstration, we'll use SQLite. For production, consider PostgreSQL with psycopg2-binary.
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

# Function to create database tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Dependency to get a database session (yields a session)
def get_db():
    with Session(engine) as session:
        yield session

# --- FastAuth Initialization ---
# Initialize FastAuth. Since we are using the default models provided by the
# library, we only need to provide the database session dependency.
# To use custom models, see the "Custom User Models" documentation.
fast_auth = FastAuth(get_db=get_db)

# --- FastAPI App Configuration ---

# Include the authentication router provided by FastAuth.
# This will add endpoints like /login/oauth, /login/signup, /users/me, etc.
app.include_router(fast_auth.get_router(), prefix="/auth") # Added a prefix for organization

# --- Startup Event to Create Tables and Initial User ---
@app.on_event("startup")
def on_startup():
    create_db_and_tables() # Ensure tables are created on app startup

    # Optional: Seed a default superuser
    with Session(engine) as session:
        crud_user = fast_auth.crud_user() # Get the CRUD handler for the user model
        first_superuser = crud_user.get_by_email(session, email=settings.FIRST_SUPERUSER)
        if not first_superuser:
            user_in = models.UserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            crud_user.create(session, obj_in=user_in)
            print(f"Created default superuser: {settings.FIRST_SUPERUSER}")


# --- Example Protected Endpoint ---
# How to protect an endpoint using FastAPI MyAuth dependencies.
from fastapi import Depends
from fastapi_myauth.api.deps import APIDependencies

# Get an instance of APIDependencies from your FastAuth object.
# This contains dependencies like `get_current_active_user`, `require_role`, etc.
deps = fast_auth.deps()

@app.get("/protected-admin-route", tags=["Protected"])
def read_admin_data(
    current_admin_user: models.UserRead = Depends(deps.require_role(["admin"]))
):
    """
    An endpoint that only users with the 'admin' role (or superusers) can access.
    """
    return {"message": f"Welcome, {current_admin_user.email}! You are an administrator."}

@app.get("/protected-user-route", tags=["Protected"])
def read_user_data(
    current_user: models.UserRead = Depends(deps.get_current_active_user)
):
    """
    An endpoint that any active, authenticated user can access.
    """
    return {"message": f"Hello, {current_user.full_name or current_user.email}! You are logged in."}

```

### 2. Run Your Application

Save the code above as `main.py` and run it using Uvicorn:

```bash
uvicorn main:app --reload
```

Your FastAPI application will start, and the authentication endpoints provided by `fastapi_myauth` will be available under `/auth`. You can access the API documentation at `http://127.0.0.1:8000/docs`.

### 3. Test the Endpoints

Navigate to `http://127.0.0.1:8000/docs` in your browser. You should see the generated API documentation.

Here are some common flows you can test:

- **Sign up a new user (if `USERS_OPEN_REGISTRATION` is True):**
  - `POST /auth/login/signup`
  - Body: `{"email": "myuser@example.com", "password": "securepassword", "full_name": "John Doe"}`
- **Login with email/password:**
  - `POST /auth/login/oauth`
  - Body (form-data): `username: myuser@example.com`, `password: securepassword`
  - This will return `access_token` and `refresh_token`.
- **Access a protected endpoint:**
  - Use the `access_token` obtained from login.
  - Click "Authorize" in the Swagger UI and paste your `Bearer <access_token>`.
  - Then try `GET /protected-user-route`.

## ⚙️ Next Steps

- **[Configuration](CONFIGURATION.md)**: Understand and customize the various settings available in `fastapi_myauth`.
- **[Custom User Models](CUSTOM_USER_MODELS.md)**: Learn how to extend the default `User` model to include application-specific fields.
- **[API Reference](API_REFERENCE.md)**: Explore all the available authentication endpoints and their functionalities.
- **Email Setup**: Configure email sending for features like password recovery and magic links. Refer to `docs/usage/CONFIGURATION.md` for `EMAILS_ENABLED` and SMTP settings.
