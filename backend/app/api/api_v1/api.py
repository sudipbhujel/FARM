from fastapi import APIRouter

from app.api.api_v1.endpoints import students, users, permissions, roles

api_router = APIRouter()
api_router.include_router(
    students.router, prefix="/students", tags=["students"])
api_router.include_router(
    users.router, prefix="/users", tags=["users"])
api_router.include_router(
    permissions.router, prefix="/permissions", tags=["permissions"]
)
api_router.include_router(
    roles.router,  prefix="/roles", tags=["roles"]
)
