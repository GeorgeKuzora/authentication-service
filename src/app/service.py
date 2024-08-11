import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.handlers import router, service
from app.api.healthz.handlers import healthz_router

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Метод для определния lifespan events приложения."""
    logger.info('Starting up kafka producer...')
    await service.start()
    yield
    logger.info('Shutting down kafka producer...')
    await service.stop()

app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.include_router(healthz_router)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
