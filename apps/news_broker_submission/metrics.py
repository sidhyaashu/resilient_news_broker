import asyncio

class Metrics:
    def __init__(self):
        self.stored = 0
        self.deduplicated = 0
        self.lock = asyncio.Lock()

    async def inc_stored(self):
        async with self.lock:
            self.stored += 1

    async def inc_dedup(self):
        async with self.lock:
            self.deduplicated += 1

    async def snapshot(self):
        async with self.lock:
            return self.stored, self.deduplicated