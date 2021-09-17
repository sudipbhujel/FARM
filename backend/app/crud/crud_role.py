from typing import List
from app.core.config import database_name, role_collection_name
from app.crud.base import CRUDBase
from app.db.mongodb import AsyncIOMotorClient
from fastapi import HTTPException


class CRUDRole(CRUDBase):
    def __init__(self, collection_name):
        super().__init__(collection_name)

    async def get_role_or_404(self, conn: AsyncIOMotorClient, id: str):
        if (role := await self.get_by_id(conn, id)) is not None:
            return role

        raise HTTPException(status_code=404, detail=f"Role {id} not found")

    async def get_role_by_name_or_404(self, conn: AsyncIOMotorClient, name: str):
        if (role := await conn[database_name][self.collection_name].find_one({"name": name})) is not None:
            return role

        raise HTTPException(status_code=404, detail=f"Role {name} not found")


role = CRUDRole(role_collection_name)
