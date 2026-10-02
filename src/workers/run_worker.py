import asyncio
import logging
from arq import create_pool
from arq.connections import RedisSettings
from src.config import settings
from src.workers import tasks

logging.basicConfig(level=settings.log_level.upper())
logger = logging.getLogger(__name__)


async def startup(ctx):
    logger.info("ARQ worker started")


async def shutdown(ctx):
    logger.info("ARQ worker shutdown")


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [
        tasks.process_webhook_message,
        tasks.send_reminder,
        tasks.send_provider_request,
        tasks.cleanup_stale_conversations,
    ]
    on_startup = startup
    on_shutdown = shutdown
    allow_abort_jobs = True


if __name__ == "__main__":
    asyncio.run(asyncio.get_event_loop().create_task(
        create_pool(WorkerSettings).main()
    ))
