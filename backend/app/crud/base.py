from datetime import datetime
from typing import List, Optional, TypeVar

from app.core.config import database_name
from app.db.mongodb import AsyncIOMotorClient
from pydantic import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)


class CRUDBase():
    def __init__(self, collection_name):
        self.collection_name = collection_name

    async def get_by_id(self, conn: AsyncIOMotorClient, id: str) -> Optional[ModelType]:
        return await conn[database_name][self.collection_name].find_one({"_id": id})

    async def get_multi(self, conn: AsyncIOMotorClient, commons: dict) -> List[ModelType]:
        pipeline = []
        match_stage = {}
        if commons["filter"] is not None:
            if "search" in commons["filter"].keys():
                match_stage = {
                    "$text": {
                        "$search": commons["filter"].pop("search")
                    },
                    **commons["filter"]
                }
            else:
                match_stage = {**commons["filter"]}

        pipeline.append({"$match": match_stage})

        # sort stage
        def convert_to_dict(lst: list):
            res_dict = {lst[i]: 1 if lst[i+1] ==
                        "ASC" else -1 for i in range(0, len(lst), 2)}
            return res_dict

        pipeline.append({"$sort": convert_to_dict(commons["sort"])})

        # add fields stage
        add_fields_stage = {"$addFields": {"id": "$_id"}}

        # unset stage
        unset_stage = {
            "$unset": ["created_at"],
        }

        # facet stage
        facet_stage = {
            "$facet": {
                "data": [
                    {"$skip": commons["range"][0]},
                    {"$limit": commons["range"][1]},
                    add_fields_stage,
                    unset_stage
                ],
                "total": [{"$count": "total"}]
            }
        }

        pipeline.append(facet_stage)

        pipeline.append({
            '$addFields': {
                'total': {
                    '$cond': [
                        {
                            '$size': '$total'
                        }, {
                            '$first': '$total.total'
                        }, 0
                    ]
                }
            }
        })

        docs = []

        async for doc in conn[database_name][self.collection_name].aggregate(pipeline):
            docs.append(doc)
        return docs[0]

    async def create(self, conn: AsyncIOMotorClient, body: dict) -> ModelType:
        now = datetime.utcnow()
        body["created_at"] = now
        body["updated_at"] = body["created_at"]
        doc = await conn[database_name][self.collection_name].insert_one(body)
        return doc

    async def update_by_id(self, conn: AsyncIOMotorClient, id: str, body: dict) -> ModelType:
        body["updated_at"] = datetime.utcnow()
        doc = await conn[database_name][self.collection_name].update_one({"_id": id}, {"$set": body})
        return doc

    async def delete(self, conn: AsyncIOMotorClient, id: str):
        doc = await conn[database_name][self.collection_name].delete_one({"_id": id})
        return doc
