from typing import List, Optional

from app.core.config import database_name, users_collection_name, role_collection_name
from app.crud import crud_role
from app.crud.base import CRUDBase
from app.db.mongodb import AsyncIOMotorClient
from app.models.user import UserInCreate, UserInDB
from fastapi import HTTPException, status
from app.crud.crud_role import role


class CRUDUser(CRUDBase):
    def __init__(self, collection_name):
        super().__init__(collection_name)

    async def get_user(self, conn: AsyncIOMotorClient, username: str) -> UserInDB:
        user = await conn[database_name][users_collection_name].find_one({"username": username})
        if user:
            return UserInDB(**user)

    async def create_user(self, conn: AsyncIOMotorClient, user: UserInCreate) -> UserInDB:
        dbuser = UserInDB(**user.dict())
        dbuser.change_password(user.password)

        await self.create(conn, dbuser.dict())

        return dbuser

    async def check_free_username_and_email(
        self, conn: AsyncIOMotorClient, username: Optional[str] = None, email: Optional[str] = None
    ):
        if username:
            user_by_username = await self.get_user(conn, username)
            if user_by_username:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="User with this username already exists"
                )

    async def get_permissions(
        self, conn: AsyncIOMotorClient, username: str
    ):
        user = await self.get_user(conn, username)
        roles = conn[database_name][role_collection_name].find({
            "name": {
                "$in": user.roles
            }
        })
        permissions = []
        async for role in roles:
            permissions = permissions + role["permissions"]

        return permissions


user = CRUDUser(users_collection_name)
