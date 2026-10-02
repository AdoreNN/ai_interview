from fastapi import APIRouter, status

from app.api.dependencies import DbSession
from app.schemas.auth import AuthResponse, SignInRequest, SignUpRequest
from app.services.auth import sign_in, sign_up


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/sign-up", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: SignUpRequest, db: DbSession) -> AuthResponse:
    return sign_up(db, payload)


@router.post("/sign-in", response_model=AuthResponse)
def login(payload: SignInRequest, db: DbSession) -> AuthResponse:
    return sign_in(db, payload)

