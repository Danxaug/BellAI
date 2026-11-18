from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.logging import get_logger
from app.core.config import get_settings
from app.db.session import init_db

logger = get_logger("lifespan")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("startup", env=settings.APP_ENV)
    await init_db()
    yield
    logger.info("shutdown")