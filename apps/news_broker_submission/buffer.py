import asyncio
from typing import List, Optional
from models import NewsItem

class NewsBuffer:
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.buffer: List[NewsItem] = []
        self.lock = asyncio.Lock()

    async def push(self, item: NewsItem):
        async with self.lock:
            if len(self.buffer) >= self.capacity:
                # Drop lowest priority (3 first)
                self.buffer.sort(key=lambda x: x.priority)
                dropped = self.buffer.pop(-1)
                print(f"Dropped: {dropped.headline} [P{dropped.priority}]")

            self.buffer.append(item)

    async def pop(self) -> Optional[NewsItem]:
        async with self.lock:
            if not self.buffer:
                return None
            return self.buffer.pop(0)

    def stats(self):
        return f"Buffered: {len(self.buffer)}"