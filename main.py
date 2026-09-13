import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime, time, timedelta

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic

from src.substitution_storage import SubstitutionStorage
from src.utils.logging import setup_logging

# --- Setup ---
setup_logging()
logger = logging.getLogger(__name__)

RUN_AT = time(hour=22, minute=0)


def seconds_until_next_run() -> float:
    now = datetime.now()
    next_run = datetime.combine(now.date(), RUN_AT)
    if next_run <= now:
        next_run += timedelta(days=1)
    return (next_run - now).total_seconds()


async def periodic_update_task():
    while True:
        await asyncio.sleep(seconds_until_next_run())

        try:
            SubstitutionStorage.update()
        except Exception as e:
            logger.error(f"Error during periodic update: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(periodic_update_task())
    logger.info("Started periodic background worker.")

    yield

    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        logger.info("Stopped periodic background worker.")


security = HTTPBasic()
app = FastAPI(title="schule-infoportal data", version="1.0.0", lifespan=lifespan)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("public/favicon.ico")


@app.get("/apple-touch-icon.png", include_in_schema=False)
async def apple_touch_icon():
    return FileResponse("public/apple-touch-icon.png")


@app.get("/")
async def root():
    return {"message": "Welcome to the Schule-Infoportal Data API"}


@app.get("/health")
async def health():
    return {"status": "ok"}
