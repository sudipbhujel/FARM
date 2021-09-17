from typing import List
from app import crud

from app.core.jwt import get_current_active_user
from app.models.user import User
from fastapi import Depends, HTTPException
from app.db.mongodb import AsyncIOMotorClient, get_database


class PermissionChecker:
    def __init__(self, permission: str) -> None:
        self.permission = permission

    async def __call__(
            self,
            user: User = Depends(get_current_active_user),
            db: AsyncIOMotorClient = Depends(get_database)
    ):
        if user.is_superuser:
            return
        permissions = await crud.user.get_permissions(db, user.username)
        if self.permission not in permissions:
            raise HTTPException(
                status_code=403, detail="Operation not permitted")


class RoleChecker:
    def __init__(self, role) -> None:
        self.role = role

    def __call__(self, user: User = Depends(get_current_active_user)):
        if self.role not in user.roles:
            raise HTTPException(
                status_code=403, detail="Operation not permitted")
