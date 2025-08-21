# needed for SessionDep and other type hints
# pyright: reportInvalidTypeForm=none

from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Body, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from fastapi_myauth import crud, models, security
from fastapi_myauth.api.deps import APIDependencies
from fastapi_myauth.config import settings
from fastapi_myauth.email import (
    send_magic_login_email,
    send_reset_password_email,
)

router = APIRouter()

"""
https://github.com/OWASP/CheatSheetSeries/blob/master/cheatsheets/Authentication_Cheat_Sheet.md
Specifies minimum criteria:
    - Change password must require current password verification to ensure that it's the legitimate user.
    - Login page and all subsequent authenticated pages must be exclusively accessed over TLS or other strong transport.
    - An application should respond with a generic error message regardless of whether:
        - The user ID or password was incorrect.
        - The account does not exist.
        - The account is locked or disabled.
    - Code should go through the same process, no matter what, allowing the application to return in approximately
      the same response time.
    - In the words of George Orwell, break these rules sooner than do something truly barbaric.

See `security.py` for other requirements.
"""


def get_login_router(
    crud_user: crud.CRUDUser,
    deps: APIDependencies,
    user_model: type[models.User],
    user_read: type[models.UserRead],
    user_create: type[models.UserCreate],
    user_update: type[models.UserUpdate],
) -> APIRouter:
    router = APIRouter()
    SessionDep = deps.SessionDep

    @router.post("/signup", response_model=user_read)
    def create_user_profile(
        *,
        db: SessionDep,
        password: Annotated[str, Body()],
        email: Annotated[EmailStr, Body()],
        full_name: str | None = Body(None),
    ) -> Any:
        """
        Create a new user without needing to be logged in.
        """
        if not settings.USERS_OPEN_REGISTRATION:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Registration is closed.",
            )
        if crud_user.get_by_email(db, email=email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This username is not available.",
            )
        user_in = user_create(password=password, email=email, full_name=full_name)
        user = crud_user.create(db, obj_in=user_in)
        return user

    @router.post("/magic/{email}")
    def login_with_magic_link(*, db: SessionDep, email: str) -> models.WebToken:
        """
        First step of a 'magic link' login. Generates two tokens: one for the
        email link and one for the client to claim later. Creates the user if
        they don't exist and registration is open.
        """
        user = crud_user.get_by_email(db, email=email)
        if not user:
            if not settings.USERS_OPEN_REGISTRATION:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Registration is closed.",
                )
            user_in = user_create(email=email)
            user = crud_user.create(db, obj_in=user_in)

        if not crud_user.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A link to activate your account has been emailed.",
            )

        tokens = security.create_magic_tokens(subject=user.id)
        if settings.EMAILS_ENABLED and user.email:
            # Send email with user.email as subject
            send_magic_login_email(email_to=user.email, token=tokens[0])

        return models.WebToken(claim=tokens[1])

    @router.post("/claim")
    def validate_magic_link(
        *,
        db: SessionDep,
        obj_in: models.WebToken,
        magic_in: Annotated[models.MagicTokenPayload, Depends(deps.get_magic_token)],
    ) -> models.Token:
        """
        Second step of a 'magic link' login. The user provides the emailed token
        in the Authorization header and the client-side token in the request body.
        """
        claim_in = deps.get_magic_token(token=obj_in.claim)

        if not (magic_in.sub and claim_in.fingerprint and magic_in.fingerprint):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login failed; invalid token structure.",
            )

        user = crud_user.get(db, id=magic_in.sub)

        if (
            (claim_in.sub == magic_in.sub)
            or (claim_in.fingerprint != magic_in.fingerprint)
            or not user
            or not crud_user.is_active(user)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login failed; invalid claim.",
            )

        if not user.email_validated:
            crud_user.validate_email(db=db, db_obj=user)

        refresh_token = None
        force_totp = bool(user.totp_secret)
        if not force_totp:
            refresh_token = security.create_refresh_token(subject=user.id)
            crud.token.create(db=db, obj_in=refresh_token, user_obj=user)

        return models.Token(
            access_token=security.create_access_token(
                subject=user.id, force_totp=force_totp
            ),
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @router.post("/oauth")
    def login_with_oauth2(
        db: SessionDep,
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    ) -> models.Token:
        """
        Standard OAuth2 compatible token login.
        """
        user = crud_user.authenticate(
            db, email=form_data.username, password=form_data.password
        )
        if not form_data.password or not user or not crud_user.is_active(user):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Login failed; incorrect email or password.",
            )

        refresh_token = None
        force_totp = bool(user.totp_secret)
        if not force_totp:
            refresh_token = security.create_refresh_token(subject=user.id)
            crud.token.create(db=db, obj_in=refresh_token, user_obj=user)

        return models.Token(
            access_token=security.create_access_token(
                subject=user.id, force_totp=force_totp
            ),
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @router.post("/new-totp", response_model=models.NewTOTPResponse)
    def request_new_totp(
        *,
        current_user: Annotated[user_model, Depends(deps.get_current_active_user)],
    ) -> Any:
        """
        Request new keys to enable TOTP on the user account.
        """
        obj_in = security.create_new_totp(label=current_user.email)
        # Remove the secret ...
        return obj_in

    @router.post("/totp")
    def login_with_totp(
        *,
        db: SessionDep,
        totp_data: models.WebToken,
        current_user: Annotated[user_model, Depends(deps.get_totp_user)],
    ) -> models.Token:
        """
        Final login validation step, using TOTP. Requires a special token
        with 'totp: true' in its payload.
        """
        if not current_user.totp_secret:
            raise HTTPException(
                status_code=400, detail="Login failed; TOTP is not enabled."
            )

        new_counter = security.verify_totp(
            token=totp_data.claim,
            secret=current_user.totp_secret,
            last_counter=current_user.totp_counter,
        )
        if not new_counter:
            raise HTTPException(
                status_code=400, detail="Login failed; unable to verify TOTP."
            )
        # Save the new counter to prevent reuse
        current_user = crud_user.update_totp_counter(
            db=db, db_obj=current_user, new_counter=new_counter
        )
        refresh_token = security.create_refresh_token(subject=current_user.id)
        crud.token.create(db=db, obj_in=refresh_token, user_obj=current_user)

        return models.Token(
            access_token=security.create_access_token(subject=current_user.id),
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @router.put("/totp")
    def enable_totp_authentication(
        *,
        db: SessionDep,
        data_in: models.EnableTOTP,
        current_user: Annotated[user_model, Depends(deps.get_current_active_user)],
    ) -> models.Msg:
        """
        Validate a TOTP code and enable TOTP for the user's account.
        """
        if current_user.hashed_password:
            user = crud_user.authenticate(
                db, email=current_user.email, password=data_in.password
            )
            if not data_in.password or not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to authenticate or activate TOTP.",
                )

        totp_in = security.create_new_totp(label=current_user.email, uri=data_in.uri)
        new_counter = security.verify_totp(
            token=data_in.claim,
            secret=totp_in.secret,
            last_counter=current_user.totp_counter,
        )
        if not new_counter:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unable to authenticate or activate TOTP.",
            )
        # Enable TOTP and save the new counter to prevent reuse
        current_user = crud_user.activate_totp(
            db=db, db_obj=current_user, totp_in=totp_in
        )
        current_user = crud_user.update_totp_counter(
            db=db, db_obj=current_user, new_counter=new_counter
        )
        return models.Msg(msg="TOTP enabled. Do not lose your recovery code.")

    @router.delete("/totp")
    def disable_totp_authentication(
        *,
        db: SessionDep,
        data_in: user_update,
        current_user: Annotated[user_model, Depends(deps.get_current_active_user)],
    ) -> models.Msg:
        """
        Disable TOTP.
        """
        if current_user.hashed_password:
            user = crud_user.authenticate(
                db, email=current_user.email, password=data_in.original
            )
            if not data_in.original or not user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Unable to authenticate or deactivate TOTP.",
                )

        crud_user.deactivate_totp(db=db, db_obj=current_user)
        return models.Msg(msg="TOTP disabled. You can re-enable it at any time.")

    @router.post("/refresh")
    def refresh_token(
        db: SessionDep,
        current_user: Annotated[user_model, Depends(deps.get_refresh_user)],
    ) -> models.Token:
        """
        Get a new access and refresh token. The provided refresh token is
        revoked upon use.
        """
        refresh_token = security.create_refresh_token(subject=current_user.id)
        crud.token.create(db=db, obj_in=refresh_token, user_obj=current_user)
        return models.Token(
            access_token=security.create_access_token(subject=current_user.id),
            refresh_token=refresh_token,
            token_type="bearer",
        )

    @router.post("/revoke", dependencies=[Depends(deps.get_refresh_user)])
    def revoke_refresh_token() -> models.Msg:
        """
        Revoke a refresh token
        """
        return models.Msg(msg="Token revoked successfully.")

    @router.post("/recover/{email}")
    def recover_password(email: str, db: SessionDep) -> models.WebToken | models.Msg:
        """
        Initiate password recovery. If the user exists and is active, an email
        is sent with a recovery link.
        """
        user = crud_user.get_by_email(db, email=email)
        if user and crud_user.is_active(user):
            tokens = security.create_magic_tokens(
                subject=user.id,
                expires_delta=timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS),
            )
            if settings.EMAILS_ENABLED:
                send_reset_password_email(
                    email_to=user.email, email=email, token=tokens[0]
                )
                return models.WebToken(claim=tokens[1])
        return models.Msg(
            msg="If that login exists, we'll send you an email to reset your password."
        )

    @router.post("/reset")
    def reset_password(
        *,
        db: SessionDep,
        new_password: Annotated[str, Body(min_length=8)],
        claim: Annotated[str, Body()],
        magic_in: Annotated[models.MagicTokenPayload, Depends(deps.get_magic_token)],
    ) -> models.Msg:
        """
        Final step of password recovery. The user provides the recovery token from
        the email header and the client-side token from the body.
        """
        claim_in = deps.get_magic_token(token=claim)

        if not (magic_in.sub and claim_in.fingerprint and magic_in.fingerprint):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password update failed; invalid token structure.",
            )

        user = crud_user.get(db, id=magic_in.sub)

        if (
            (claim_in.sub == magic_in.sub)
            or (claim_in.fingerprint != magic_in.fingerprint)
            or not user
            or not crud_user.is_active(user)
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password update failed; invalid claim.",
            )
        # Update the password
        hashed_password = security.get_password_hash(new_password)
        user.hashed_password = hashed_password
        db.add(user)
        db.commit()
        return models.Msg(msg="Password updated successfully.")

    return router
