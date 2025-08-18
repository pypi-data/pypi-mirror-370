from typing import Generic, TypeVar

from pydantic import EmailStr
from sqlmodel import Session, select

from fastapi_myauth.models import NewTOTP, User, UserCreate, UserUpdate
from fastapi_myauth.security import get_password_hash, verify_password

from .base import CRUDBase

ModelType = TypeVar("ModelType", bound=User)
CreateSchemaType = TypeVar("CreateSchemaType", bound=UserCreate)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=UserUpdate)


class CRUDUser(
    CRUDBase[ModelType, CreateSchemaType, UpdateSchemaType],
    Generic[ModelType, CreateSchemaType, UpdateSchemaType],
):
    def get_by_email(self, db: Session, *, email: str) -> ModelType | None:
        return db.exec(select(self.model).where(self.model.email == email)).first()

    def create(self, db: Session, *, obj_in: CreateSchemaType) -> ModelType:
        """
        Creates a new user, hashing the password if provided.
        """
        create_data = obj_in.model_dump()
        # Handle password separately
        password = create_data.pop("password", None)
        if password:
            create_data["hashed_password"] = get_password_hash(password)
        else:
            create_data["hashed_password"] = None

        db_obj = self.model(**create_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelType, obj_in: UpdateSchemaType
    ) -> ModelType:
        update_data = obj_in.model_dump(exclude_unset=True)
        if update_data.get("password"):
            hashed_password = get_password_hash(update_data["password"])
            del update_data["password"]
            update_data["hashed_password"] = hashed_password
        if update_data.get("email") and db_obj.email != update_data["email"]:
            update_data["email_validated"] = False

        return super().update(db, db_obj=db_obj, obj_in=update_data)

    def authenticate(
        self, db: Session, *, email: str, password: str | None
    ) -> ModelType | None:
        user = self.get_by_email(db, email=email)
        if not user:
            return None
        if not verify_password(
            plain_password=password, hashed_password=user.hashed_password
        ):
            return None
        return user

    def validate_email(self, db: Session, *, db_obj: ModelType) -> ModelType:
        obj_in = {"email_validated": True}
        return super().update(db=db, db_obj=db_obj, obj_in=obj_in)

    def activate_totp(
        self, db: Session, *, db_obj: ModelType, totp_in: NewTOTP
    ) -> ModelType:
        obj_in = {"totp_secret": totp_in.secret}
        return super().update(db=db, db_obj=db_obj, obj_in=obj_in)

    def deactivate_totp(self, db: Session, *, db_obj: ModelType) -> ModelType:
        obj_in = {"totp_secret": None, "totp_counter": None}
        return super().update(db=db, db_obj=db_obj, obj_in=obj_in)

    def update_totp_counter(
        self, db: Session, *, db_obj: ModelType, new_counter: int
    ) -> ModelType:
        obj_in = {"totp_counter": new_counter}
        return super().update(db=db, db_obj=db_obj, obj_in=obj_in)

    def toggle_user_state(
        self, db: Session, *, user_email: EmailStr
    ) -> ModelType | None:
        db_obj = self.get_by_email(db, email=user_email)
        if not db_obj:
            return None
        return super().update(
            db=db, db_obj=db_obj, obj_in={"is_active": not db_obj.is_active}
        )

    @staticmethod
    def has_password(user: ModelType) -> bool:
        return bool(user.hashed_password)

    @staticmethod
    def is_active(user: ModelType) -> bool:
        return user.is_active

    @staticmethod
    def is_superuser(user: ModelType) -> bool:
        return user.is_superuser

    @staticmethod
    def is_email_validated(user: ModelType) -> bool:
        return user.email_validated
