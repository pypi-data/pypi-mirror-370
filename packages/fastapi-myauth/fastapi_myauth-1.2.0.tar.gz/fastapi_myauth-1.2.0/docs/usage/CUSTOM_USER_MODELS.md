# ✍️ Customizing User Models

One of the key strengths of `FastAPI MyAuth` is its flexibility in handling custom user models. You often need to store more information about a user than just email and password (e.g., `language`, `timezone`, `preferences`). This guide explains how to extend the default `User` model (`fastapi_myauth.models.User`) and seamlessly integrate it with the library.

`FastAuth` is generic over four types of user models:

- `UserT`: Your primary database model (inherits from `SQLModel`, often extending `fastapi_myauth.models.User`). This is the model that interacts directly with your database.
- `UserReadT`: Pydantic model for reading/returning user data from API endpoints. This is what clients receive.
- `UserCreateT`: Pydantic model for creating new users via API. This defines what data the client sends when signing up.
- `UserUpdateT`: Pydantic model for updating existing user data via API. This defines what data the client sends when updating their profile.

## 🚶‍♂️ Step-by-Step Customization

### 1. Define Your Custom User Models

Start by creating your own models that inherit from the base models provided by `fastapi_myauth.models`.

Let's say you want to add a `language` field to your users.

```python
# app/models.py (or similar path in your project)
from datetime import datetime
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel, Relationship
from pydantic import EmailStr

# Import base models from fastapi_myauth
from fastapi_myauth.models import User as BaseUser
from fastapi_myauth.models import UserCreate as BaseUserCreate
from fastapi_myauth.models import UserRead as BaseUserRead
from fastapi_myauth.models import UserUpdate as BaseUserUpdate
from fastapi_myauth.models import RefreshToken # Needed for relationship

# --- Custom User Database Model ---
# This class needs to be a SQLModel table.
# It MUST inherit from BaseUser and define `table=True`
# It's crucial that `refresh_tokens` Relationship matches the one defined internally by FastAuth.
class CustomUser(BaseUser, table=True):
    # All fields from BaseUser (id, email, hashed_password, created, modified, etc.) are inherited.
    # Add your custom fields here:
    language: str = Field(default="en", max_length=10) # Example custom field

    # The 'refresh_tokens' relationship is managed by FastAuth, ensure it's here
    # and points to the RefreshToken model.
    refresh_tokens: list["RefreshToken"] = Relationship(
        back_populates="authenticates", cascade_delete=True
    )

# --- Custom User Pydantic Models for API operations ---

# For creation: include fields that can be set when a user signs up/is created
class CustomUserCreate(BaseUserCreate):
    language: str | None = None # Allow language to be optional on creation

# For reading: include fields you want to expose when fetching user data
class CustomUserRead(BaseUserRead):
    language: str # Ensure language is included when reading

# For updating: include fields that can be updated by the user or admin
class CustomUserUpdate(BaseUserUpdate):
    language: str | None = None # Allow language to be optional on update
    # Note: password, full_name, email are inherited from BaseUserUpdate
```

### 2. Pass Your Custom Models to `FastAuth`

When initializing `FastAuth`, pass your custom models to it.

```python
# main.py (or your FastAPI app's entry point)
from fastapi import FastAPI
from sqlmodel import Session, create_engine, SQLModel

from fastapi_myauth.auth import FastAuth
from fastapi_myauth.config import settings

# Import your custom models
from app.models import CustomUser, CustomUserCreate, CustomUserRead, CustomUserUpdate

app = FastAPI()

# --- Database Setup (same as basic example) ---
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_db():
    with Session(engine) as session:
        yield session

# --- FastAuth Initialization with CUSTOM models ---
fast_auth = FastAuth(
    get_db=get_db,
    user_model=CustomUser,        # Your custom SQLModel User
    user_read=CustomUserRead,     # Your custom Pydantic Read model
    user_create=CustomUserCreate, # Your custom Pydantic Create model
    user_update=CustomUserUpdate, # Your custom Pydantic Update model
)

# --- Startup Event to Create Tables and Initial User ---
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

    with Session(engine) as session:
        crud_user = fast_auth.crud_user() # Get the CRUD handler for the custom user model
        first_superuser = crud_user.get_by_email(session, email=settings.FIRST_SUPERUSER)
        if not first_superuser:
            user_in = CustomUserCreate(
                email=settings.FIRST_SUPERUSER,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
                language="en", # Now you can set your custom field!
                full_name="Super Admin"
            )
            crud_user.create(session, obj_in=user_in)
            print(f"Created default superuser: {settings.FIRST_SUPERUSER}")


# --- Include the authentication router ---
app.include_router(fast_auth.get_router(), prefix="/auth")

# --- Example Protected Endpoint using CustomUserRead ---
from fastapi import Depends
deps = fast_auth.deps()

@app.get("/me-custom-data", response_model=CustomUserRead, tags=["User"])
def read_current_user_with_custom_data(
    current_user: CustomUserRead = Depends(deps.get_current_active_user)
):
    """
    Get current user's data, including custom fields like language.
    Note: The return type must match the user_read model you passed to FastAuth.
    """
    return current_user

```

### 3. Update Database Schema (if necessary)

If you're adding new fields to your `User` model, you'll need to update your database schema. If you're using `alembic` (recommended for production), you'd generate a migration:

```bash
# Assuming Alembic is set up for your project
alembic revision --autogenerate -m "Add language field to user"
alembic upgrade head
```

If you're just starting, `SQLModel.metadata.create_all(engine)` will create the tables including your new fields.

## 💡 Important Considerations

- **`UserT` must be a SQLModel `table=True`**: Your primary user model (`CustomUser` in the example) _must_ be defined as a SQLModel table (`class CustomUser(BaseUser, table=True):`).
- **Relationship `refresh_tokens`**: Your `UserT` model _must_ include the `refresh_tokens` relationship as shown in the example (`refresh_tokens: list["RefreshToken"] = Relationship(...)`). This is crucial for `FastAuth`'s internal token management.
- **Inheritance**: Always inherit from the respective `fastapi_myauth.models` base classes (`BaseUser`, `BaseUserCreate`, `BaseUserRead`, `BaseUserUpdate`). This ensures you retain all essential fields and properties expected by `FastAuth`.
- **Field Type Matching**: Ensure that the types of overridden or added fields in your `UserCreateT`, `UserReadT`, and `UserUpdateT` models are compatible with your `UserT` (database) model. Pydantic handles validation, so define types accurately.
- **Field `hashed_password` in `UserReadT`**: `fastapi_myauth` expects `UserReadT` to have a boolean field named `hashed_password` (aliased from `password`) and `totp_secret` (aliased from `totp`). This boolean indicates the presence of a password/TOTP secret _without exposing the actual hash/secret_. Ensure your `UserReadT` maintains this. The base `models.UserRead` takes care of this via `@field_validator`.
- **`crud_user` Method**: `fast_auth.crud_user()` returns a CRUD handler specifically typed for your custom user model, so you can interact with your database safely.

By following these steps, you can confidently customize your user model to fit your application's unique data requirements while leveraging the robust authentication features of `FastAPI MyAuth`.
