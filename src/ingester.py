import asyncio
import json
import logging
import websockets
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

class NewsIngester:
    """
    Handles connection to the mock source feed, processes incoming streams,
    and manages reconnection with Exponential Backoff.
    """
    def __init__(self, url: str, token: str):
        self.url = url
        self.token = token
        self.backoff_factor = 2 # e.g. delay = backoff_factor ** attempt
        self.max_attempts = 5

    async def connect(self) -> AsyncGenerator[str, None]:
        """
        Connects to the WebSocket server, performs handshake, and streams messages.
        
        Candidates: Implement your EXPONENTIAL BACKOFF logic here to survive
        the "Chaos" drops. Use try/except to catch connection issues.
        """
        # Skeleton connection loop:
        attempt = 0
        while attempt < self.max_attempts:
            try:
                logger.info(f"Connecting to {self.url} (Attempt {attempt + 1})")
                async with websockets.connect(self.url) as websocket:
                    # Send Handshake
                    await websocket.send(json.dumps({"token": self.token}))
                    
                    # Receive response
                    resp = await websocket.recv()
                    logger.info(f"Handshake response: {resp}")
                    
                    # Stream items
                    while True:
                        try:
                            msg = await websocket.recv()
                            # Yield raw message string for processing/cleaning
                            yield msg 
                        except websockets.exceptions.ConnectionClosed:
                            logger.warning("Connection closed by server")
                            break # triggers reconnect backoff
                        
                    # Reset attempt count upon successful operations inside stream
                    attempt = 0 
                    
            except Exception as e:
                logger.error(f"Failed to connect or read: {e}")
                # Candidates: Implement Backoff wait duration calculation here
                wait = 2 ** attempt 
                logger.info(f"Waiting {wait}s before reconnecting...")
                await asyncio.sleep(wait)
                attempt += 1

        logger.critical("Max reconnect attempts reached. Exiting.")
