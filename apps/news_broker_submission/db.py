from motor.motor_asyncio import AsyncIOMotorClient
from apps.news_broker_submission.config import MONGO_URI, DB_NAME, COLLECTION_NAME


class MongoDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.collection = self.client[DB_NAME][COLLECTION_NAME]

    async def insert(self, item: dict):
        await self.collection.insert_one(item)