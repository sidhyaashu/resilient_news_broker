import asyncio
import logging
from typing import List, Optional
from apps.news_broker_submission.models import NewsItem

logger = logging.getLogger(__name__)

class NewsBuffer:
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        self.buffer: List[NewsItem] = []
        self.lock = asyncio.Lock()

    async def push(self, item: NewsItem):
        async with self.lock:
            if len(self.buffer) >= self.capacity:
                self.buffer.sort(key=lambda x: (-x.priority, x.timestamp))

                dropped = self.buffer.pop(0)

                logger.warning(
                    f"Dropped item: {dropped.headline} [P{dropped.priority}]"
                )

            self.buffer.append(item)
            logger.debug(f"Buffered: {item.headline} [P{item.priority}]")

    async def pop(self) -> Optional[NewsItem]:
        async with self.lock:
            if not self.buffer:
                return None
            return self.buffer.pop(0)

    def stats(self):
        count_p1 = len([x for x in self.buffer if x.priority == 1])
        count_p2 = len([x for x in self.buffer if x.priority == 2])
        count_p3 = len([x for x in self.buffer if x.priority == 3])

        return (
            f"Buffered: {len(self.buffer)} "
            f"(P1: {count_p1}, P2: {count_p2}, P3: {count_p3})"
        )