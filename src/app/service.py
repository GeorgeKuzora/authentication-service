import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from prometheus_client import make_asgi_app
from starlette.middleware.base import BaseHTTPMiddleware

from app.api.handlers import router
from app.api.healthz.handlers import healthz_router
from app.core.authentication import AuthService
from app.core.config.config import get_auth_config, get_settings
from app.core.interfaces import MetricsClient
from app.external.kafka import KafkaProducer
from app.external.postgres.storage import DBStorage
from app.external.redis import TokenCache
from app.metrics.metrics import NoneClient, PrometheusClient
from app.metrics.tracing import get_tracer, tracing_middleware
from app.middleware import middleware

logger = logging.getLogger(__name__)


def get_service() -> AuthService:
    """
    Инициализирует сервис.

    :return: Объект сервиса.
    :rtype: AuthService
    """
    cache = TokenCache()
    persistent = DBStorage()
    config = get_auth_config()
    queue = KafkaProducer()
    return AuthService(
        repository=persistent, cache=cache, config=config, producer=queue,
    )


metrics_app = make_asgi_app()


def get_metrics(app: FastAPI) -> MetricsClient:
    """
    Инициализирует клиент метрик.

    :param app: Объект приложения.
    :type app: FastAPI
    :return: Объект клиента метрик.
    :rtype: MetricsClient
    """
    settings = get_settings()
    if settings.metrics.enabled is True:
        return PrometheusClient(app)
    return NoneClient()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Метод для определения lifespan events приложения.

    :param app: Объект приложения.
    :type app: FastAPI
    :yield: Состояние запроса.
    :ytype: TypedDict
    """
    service = get_service()
    app.service = service  # type: ignore # app has **extras specially for it
    metrics_client = get_metrics(metrics_app)
    tracer = get_tracer()
    logger.info('Starting up kafka producer...')
    await service.start()
    yield {
        'metrics_client': metrics_client,
        'tracer': tracer,
    }
    logger.info('Shutting down kafka producer...')
    await service.stop()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    BaseHTTPMiddleware, dispatch=middleware.ready_metric_middleware,
)
app.add_middleware(
    BaseHTTPMiddleware, dispatch=middleware.duration_metric_middleware,
)
app.add_middleware(
    BaseHTTPMiddleware, dispatch=middleware.count_metric_middleware,
)
app.add_middleware(
    BaseHTTPMiddleware, dispatch=middleware.auth_metric_middleware,
)
app.add_middleware(
    BaseHTTPMiddleware, dispatch=tracing_middleware,
)

app.mount('/metrics', metrics_app)  # type: ignore
app.include_router(router)
app.include_router(healthz_router)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
