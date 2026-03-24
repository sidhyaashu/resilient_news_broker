from motor.motor_asyncio import AsyncIOMotorClient

class MongoDB:
    def __init__(self):
        self.client = AsyncIOMotorClient("mongodb://localhost:27017")
        self.collection = self.client["news_db"]["news"]

    async def insert(self, item):
        await self.collection.insert_one(item.dict())