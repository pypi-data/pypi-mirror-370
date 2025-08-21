from __future__ import annotations

from sqlmodel import Session

from ..config import settings
from ..models import RefreshToken, RefreshTokenCreate, RefreshTokenUpdate, User
from .base import CRUDBase


class CRUDToken(CRUDBase[RefreshToken, RefreshTokenCreate, RefreshTokenUpdate]):
    # Everything is user-dependent
    def create(self, db: Session, *, obj_in: str, user_obj: User) -> RefreshToken:
        db_obj = db.get(self.model, obj_in)
        if db_obj:
            return db_obj
        obj = RefreshTokenCreate(token=obj_in, authenticates_id=user_obj.id)
        return super().create(db=db, obj_in=obj)

    def get(self, *, user: User, token: str) -> RefreshToken | None:
        for refresh_token in user.refresh_tokens:  # type: ignore
            if refresh_token.token == token:
                return refresh_token
        return None

    def get_multi(
        self, *, user: User, page: int = 0, page_break: bool = False
    ) -> list[RefreshToken]:
        db_objs = user.refresh_tokens  # type: ignore
        if not page_break:
            if page > 0:
                db_objs = db_objs[page * settings.MULTI_MAX + 1 :]
            db_objs = db_objs[: settings.MULTI_MAX]
        return db_objs

    def remove(self, db: Session, *, db_obj: RefreshToken) -> None:
        db.delete(db_obj)
        db.commit()
        return None


token = CRUDToken(RefreshToken)
