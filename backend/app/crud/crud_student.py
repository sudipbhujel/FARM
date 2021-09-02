from app.core.config import student_collection_name
from app.crud.base import CRUDBase
from app.db.mongodb import AsyncIOMotorClient
from fastapi import HTTPException, Response, status


class CRUDStudent(CRUDBase):
    def __init__(self, collection_name):
        super().__init__(collection_name)

    async def get_student_or_404(self, conn: AsyncIOMotorClient, id: str):
        if (student := await self.get_by_id(conn, id)) is not None:
            return student

        raise HTTPException(status_code=404, detail=f"Student {id} not found")


student = CRUDStudent(student_collection_name)
