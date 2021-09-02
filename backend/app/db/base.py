import os

import motor.motor_asyncio

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ.get("MONGOURI"))

print("MONGO => ", os.environ.get("MONGOURI"))

db = client.college
