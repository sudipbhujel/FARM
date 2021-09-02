from app.core.config import users_collection_name, database_name
from app.crud.base import CRUDBase
from app.db.mongodb import AsyncIOMotorClient
from app.models.user import UserInDB
from fastapi import HTTPException


class CRUDUser(CRUDBase):
    def __init__(self, collection_name):
        super().__init__(collection_name)

    async def get_user(self, conn: AsyncIOMotorClient, username: str) -> UserInDB:
        user = await conn[database_name][users_collection_name].find_one({"username": username})
        if user:
            return UserInDB(**user)


user = CRUDUser(users_collection_name)
