from contextlib import asynccontextmanager
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI

from aibackend.api.ingestion import router as ingestion_router
from aibackend.api.memory_card import router as memory_card_router
from aibackend.db.connection import AsyncSessionLocal
from aibackend.logging_config import setup_logging
from aibackend.services.memory_card import send_all_image

setup_logging()


async def scheduled_queue_images() -> None:
    """Run the image queue job with its own database session."""
    async with AsyncSessionLocal() as db:
        await send_all_image(db)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = AsyncIOScheduler(
        timezone="Asia/Kuala_Lumpur",
    )

    scheduler.add_job(
        scheduled_queue_images,
        trigger=IntervalTrigger(minutes=5),
        id="memory_card_queue_images",
        next_run_time=datetime.now(scheduler.timezone),
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()

    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(
    title="AI Backend",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(ingestion_router)
app.include_router(memory_card_router)
