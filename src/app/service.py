import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.handlers import router
from app.api.healthz.handlers import healthz_router
from app.core.authentication import AuthService
from app.core.config.config import get_auth_config, get_settings
from app.core.interfaces import MetricsClient
from app.external.kafka import KafkaProducer
from app.external.postgres.storage import DBStorage
from app.external.redis import TokenCache
from app.metrics.metrics import NoneClient, PrometheusClient

logger = logging.getLogger(__name__)


def get_service() -> AuthService:
    """Инициализирует сервис."""
    cache = TokenCache()
    persistent = DBStorage()
    config = get_auth_config()
    queue = KafkaProducer()
    return AuthService(
        repository=persistent, cache=cache, config=config, producer=queue,
    )


def get_metrics() -> MetricsClient:
    """Инициализирует клиент метрик."""
    settings = get_settings()
    if settings.metrics.enabled is True:
        return PrometheusClient()
    return NoneClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Метод для определения lifespan events приложения."""
    service = get_service()
    app.service = service  # type: ignore # app has **extras specially for it
    metrics_client = get_metrics()
    if metrics_client.app is not None:  # type: ignore
        app.mount('/metrics', metrics_client.app)  # type: ignore
    logger.info('Starting up kafka producer...')
    await service.start()
    yield {
        'metrics_client': metrics_client,
    }
    logger.info('Shutting down kafka producer...')
    await service.stop()

app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.include_router(healthz_router)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
