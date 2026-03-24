import asyncio
import json
import logging
from pydantic import ValidationError

# Correct absolute/relative imports based on execution context
from src.models import NewsItem
from src.ingester import NewsIngester
from src.deduplicator import NewsDeduplicator
from src.buffer import NewsBuffer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

async def metrics_reporter(buffer: NewsBuffer):
    """
    Periodically reports metrics every 60 seconds.
    Candidates: Maintain proper counters for stored/dropped/deduplicated.
    """
    stored_count = 0
    dedup_count = 0
    
    while True:
        await asyncio.sleep(60)
        # Candidates: Update these counts based on your logic execution
        stats = buffer.stats()
        logger.info(f"--- METRICS --- Stored: {stored_count} | Deduplicated/Dropped: {dedup_count} | {stats}")

async def main():
    # Configuration
    WS_URL = "ws://localhost:8888/ws"
    TOKEN = "test-session-chaos"
    
    # Initialize components
    ingester = NewsIngester(WS_URL, TOKEN)
    deduplicator = NewsDeduplicator(threshold=0.8)
    buffer = NewsBuffer(capacity=100)

    # Start metrics background task
    asyncio.create_task(metrics_reporter(buffer))

    logger.info("Starting Resilient News Broker...")

    # Consume stream
    async for raw_msg in ingester.connect():
        try:
            # 1. Clean / Parse JSON
            data = json.loads(raw_msg)
            item = NewsItem(**data)
            
            # 2. Fuzzy Deduplication
            if deduplicator.is_duplicate(item.headline):
                logger.debug(f"Duplicate dropped: {item.headline}")
                # Increment dedup counter
                continue
                
            # 3. Buffer Persistence (Circuit Breaker)
            await buffer.push(item)
            logger.info(f"Processed: {item.headline} [P{item.priority}]")

        except json.JSONDecodeError:
            logger.warning(f"Malformed JSON stream item ignored: {raw_msg[:50]}...")
        except ValidationError as e:
            logger.warning(f"Schema Validation failed for item: {e}")
        except Exception as e:
            logger.error(f"Unexpected processing error: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Broker stopped by user")
