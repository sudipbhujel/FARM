from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings
from .mongodb import db


async def connect_to_mongo():
    db.client = AsyncIOMotorClient(str(settings.MONGODB_URL))


async def close_mongo_connection():
    db.client.close()
