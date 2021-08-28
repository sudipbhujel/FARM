from datetime import datetime
from typing import List, Optional, TypeVar

from app.db.base import db
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class CRUDBase():
    def __init__(self, collection):
        self.collection = collection

    async def get(self, id: str) -> Optional[ModelType]:
        return await db[self.collection].find_one({"_id": id})

    async def get_multi(
        self, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        docs = []
        pipeline = [
            {"$skip": skip},
            {"$limit": limit}
        ]
        async for doc in db[self.collection].aggregate(pipeline):
            docs.append(doc)
        return docs

    async def create(self, body: dict) -> ModelType:
        now = datetime.utcnow()
        body["created_at"] = now
        body["updated_at"] = body["created_at"]
        doc = await db[self.collection].insert_one(body)
        return doc

    async def update(self, id: str, body: dict) -> ModelType:
        body["updated_at"] = datetime.utcnow()
        doc = await db[self.collection].update_one({"_id": id}, {"$set": body})
        return doc

    async def delete(self, id: str):
        doc = await db[self.collection].delete_one({"_id": id})
        return doc
