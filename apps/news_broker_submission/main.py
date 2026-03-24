import asyncio
import json
import logging
from pydantic import ValidationError

from apps.news_broker_submission.models import NewsItem
from apps.news_broker_submission.ingester import NewsIngester
from apps.news_broker_submission.deduplicator import NewsDeduplicator
from apps.news_broker_submission.buffer import NewsBuffer
from apps.news_broker_submission.db import MongoDB

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

stored_count = 0
dedup_count = 0


async def db_worker(buffer: NewsBuffer, db: MongoDB):
    global stored_count

    while True:
        item = await buffer.pop()

        if not item:
            await asyncio.sleep(0.1)
            continue

        try:
            await db.insert(item)
            stored_count += 1

        except Exception as e:
            await buffer.push(item)
            logger.warning(f"DB error, retrying: {e}")
            await asyncio.sleep(2)


async def metrics(buffer: NewsBuffer):
    global stored_count, dedup_count

    while True:
        await asyncio.sleep(60)
        logger.info(
            f"--- METRICS --- Stored: {stored_count} | "
            f"Deduplicated: {dedup_count} | {buffer.stats()}"
        )


async def main():
    WS_URL = "ws://localhost:8888/ws"
    TOKEN = "test-session-chaos"

    ingester = NewsIngester(WS_URL, TOKEN)
    deduplicator = NewsDeduplicator()
    buffer = NewsBuffer()
    db = MongoDB()

    # background workers
    asyncio.create_task(db_worker(buffer, db))
    asyncio.create_task(metrics(buffer))

    logger.info("Starting Resilient News Broker...")

    async for raw_msg in ingester.connect():
        try:
            data = json.loads(raw_msg)
            item = NewsItem(**data)

            if deduplicator.is_duplicate(item.headline):
                dedup_count += 1
                continue

            await buffer.push(item)

        except json.JSONDecodeError:
            logger.warning(f"Malformed JSON ignored: {raw_msg[:50]}")
        except ValidationError as e:
            logger.warning(f"Validation failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())