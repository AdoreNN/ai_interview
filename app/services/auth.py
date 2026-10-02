from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, normalize_email, verify_password
from app.models.user import User
from app.schemas.auth import AuthResponse, SignInRequest, SignUpRequest


AUTHENTICATION_ERROR = "Invalid email or password"


def build_auth_response(user: User) -> AuthResponse:
    return AuthResponse(
        id=user.id,
        email=user.email,
        access_token=create_access_token(user.id),
    )


def sign_up(db: Session, payload: SignUpRequest) -> AuthResponse:
    email = normalize_email(str(payload.email))
    if db.scalar(select(User).where(User.email == email)) is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email is already registered")

    user = User(email=email, password_hash=hash_password(payload.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email is already registered"
        ) from exc
    db.refresh(user)
    return build_auth_response(user)


def sign_in(db: Session, payload: SignInRequest) -> AuthResponse:
    email = normalize_email(str(payload.email))
    user = db.scalar(select(User).where(User.email == email))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=AUTHENTICATION_ERROR,
            headers={"WWW-Authenticate": "Bearer"},
        )
    return build_auth_response(user)

