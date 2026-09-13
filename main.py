import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.security import HTTPBasic

from src.utils.logging import setup_logging

# --- Setup ---
setup_logging()
logger = logging.getLogger(__name__)

INTERVAL_HOURS = 10


async def periodic_update_task():
    while True:
        try:
            logger.info("Starting periodic update...")
            logger.info("Periodic update completed successfully.")
        except Exception as e:
            logger.error(f"Error during periodic update: {e}")

        await asyncio.sleep(INTERVAL_HOURS * 3600)


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


app = FastAPI(title="Schule-Infoportal Data", version="1.0.0", lifespan=lifespan)
security = HTTPBasic()


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
