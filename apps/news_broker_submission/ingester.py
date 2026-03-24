import asyncio
import json
import logging
import websockets
import random
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

class NewsIngester:
    def __init__(self, url: str, token: str, max_attempts: int = 5, backoff_factor: int = 2):
        self.url = url
        self.token = token
        self.max_attempts = max_attempts
        self.backoff_factor = backoff_factor

    async def connect(self) -> AsyncGenerator[str, None]:
        attempt = 0

        while attempt < self.max_attempts:
            try:
                logger.info(f"Connecting to {self.url} (Attempt {attempt + 1})")

                async with websockets.connect(self.url) as websocket:
                    
                    # Handshake
                    await websocket.send(json.dumps({"token": self.token}))
                    resp = await websocket.recv()
                    logger.info(f"Handshake response: {resp}")

                    # Reset attempts after success
                    attempt = 0

                    while True:
                        msg = await websocket.recv()
                        yield msg

            except Exception as e:
                # All connection issues handled here
                logger.warning(f"Connection issue: {e}")

                wait = min(
                    60,
                    (self.backoff_factor ** attempt) + random.random()
                )

                logger.info(f"Retrying in {wait:.2f}s...")
                await asyncio.sleep(wait)

                attempt += 1

        logger.critical("Max reconnect attempts reached. Exiting.")