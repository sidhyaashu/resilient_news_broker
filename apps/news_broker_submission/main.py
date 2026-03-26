import asyncio
import json
import logging
from pydantic import ValidationError

from apps.news_broker_submission.models import NewsItem
from apps.news_broker_submission.ingester import NewsIngester
from apps.news_broker_submission.deduplicator import NewsDeduplicator
from apps.news_broker_submission.buffer import NewsBuffer
from apps.news_broker_submission.db import MongoDB
from apps.news_broker_submission.metrics import Metrics
from apps.news_broker_submission.config import (
    WS_URL,
    TOKEN,
    BUFFER_CAPACITY,
    DEDUP_THRESHOLD,
    WINDOW_SIZE,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MAX_RETRIES = 5


async def db_worker(buffer: NewsBuffer, db: MongoDB, metrics: Metrics):
    while True:
        item = await buffer.pop()

        if not item:
            await asyncio.sleep(0.1)
            continue

        try:
            await db.insert(item)
            await metrics.inc_stored()

        except Exception as e:
            item.retry_count += 1

            if item.retry_count > MAX_RETRIES:
                logger.error(f"Dropped after retries: {item.headline}")
                continue

            await buffer.push(item)

            logger.warning(
                f"DB retry {item.retry_count} for '{item.headline}': {e}"
            )

            await asyncio.sleep(min(2 ** item.retry_count, 30))


async def metrics_reporter(buffer: NewsBuffer, metrics: Metrics):
    while True:
        await asyncio.sleep(60)

        stored, dedup = await metrics.snapshot()

        logger.info(
            f"--- METRICS --- Stored: {stored} | "
            f"Deduplicated: {dedup} | {buffer.stats()}"
        )


async def main():
    ingester = NewsIngester(WS_URL, TOKEN)

    deduplicator = NewsDeduplicator(
        threshold=DEDUP_THRESHOLD,
        window_size=WINDOW_SIZE
    )

    buffer = NewsBuffer(capacity=BUFFER_CAPACITY)
    db = MongoDB()
    metrics = Metrics()

    asyncio.create_task(db_worker(buffer, db, metrics))
    asyncio.create_task(metrics_reporter(buffer, metrics))

    logger.info("Starting Resilient News Broker...")

    async for raw_msg in ingester.connect():
        try:
            data = json.loads(raw_msg)

            item = NewsItem(**data)

            if deduplicator.is_duplicate(item.headline):
                await metrics.inc_dedup()
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