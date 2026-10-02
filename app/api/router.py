from fastapi import APIRouter

from app.api.routes import auth, interviews, resumes, sessions


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(sessions.router)
api_router.include_router(resumes.router)
api_router.include_router(interviews.router)
