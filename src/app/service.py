import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.handlers import router
from app.api.healthz.handlers import healthz_router
from app.core.authentication import AuthService
from app.core.config import get_auth_config
from app.external.in_memory_repository import InMemoryRepository
from app.external.kafka import KafkaProducer
from app.external.redis import TokenCache

logger = logging.getLogger(__name__)


def get_service() -> AuthService:
    """Инициализирует сервис."""
    cache = TokenCache()
    persistent = InMemoryRepository()
    config = get_auth_config()
    queue = KafkaProducer()
    return AuthService(
        repository=persistent, cache=cache, config=config, producer=queue,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Метод для определения lifespan events приложения."""
    service = get_service()
    logger.info('Starting up kafka producer...')
    app.service = service  # type: ignore # app has **extras specially for it
    await service.start()
    yield
    logger.info('Shutting down kafka producer...')
    await service.stop()

app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.include_router(healthz_router)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
