import logging
import asyncio
from typing import Optional, List
from src.models import NewsItem

logger = logging.getLogger(__name__)

class NewsBuffer:
    """
    In-memory bounded buffer to hold news items when database is unreachable.
    Drops Priority 3 items first when capacity is reached.
    """
    def __init__(self, capacity: int = 100):
        self.capacity = capacity
        # Candidates: Use `asyncio.Queue` or list or deque.
        # Track items by priority to implement Drop Strategy
        self.buffer: List[NewsItem] = []

    async def push(self, item: NewsItem):
        """
        Adds item to buffer.
        Candidates: Implement Drop Strategy if len(self.buffer) >= self.capacity
        Keep Priority 1, drop Priority 3 over others.
        """
        if len(self.buffer) >= self.capacity:
            logger.warning("Buffer FULL. Triggering Drop Strategy...")
            # Examples:
            # self.buffer.sort(key=lambda x: x.priority) 
            # item_to_drop = self.buffer.pop(-1) # pop lowest priority (highest number)
            # logger.info(f"Dropped item {item_to_drop.headline}")
            return # Skip adding for skeleton

        self.buffer.append(item)

    async def pop(self) -> Optional[NewsItem]:
        """Returns the next item to process/insert into DB."""
        if not self.buffer:
            return None
        return self.buffer.pop(0)

    def stats(self) -> str:
        count_p1 = len([x for x in self.buffer if x.priority == 1])
        count_p2 = len([x for x in self.buffer if x.priority == 2])
        count_p3 = len([x for x in self.buffer if x.priority == 3])
        return f"Current Buffered: {len(self.buffer)} (P1: {count_p1}, P2: {count_p2}, P3: {count_p3})"
P1_COUNT = 0
P2_COUNT = 0
P3_COUNT = 0
# candidates to define stats properly
