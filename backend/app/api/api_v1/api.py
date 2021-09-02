from fastapi import APIRouter

from app.api.api_v1.endpoints import students, authentications

api_router = APIRouter()
api_router.include_router(
    students.router, prefix="/students", tags=["students"])
api_router.include_router(
    authentications.router, prefix="/users", tags=["authentications"])
