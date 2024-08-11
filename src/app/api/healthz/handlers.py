import logging

from fastapi import APIRouter

from app.api.handlers import service
from app.core.errors import ServerError

logger = logging.getLogger(__name__)

healthz_router = APIRouter(prefix='/healthz', tags=['healthz'])

up_message = {'message': 'service is up'}
ready_message = {'message': 'service is ready'}


@healthz_router.get('/up')
async def up_check() -> dict[str, str]:
    """Healthcheck для сервера сервиса."""
    return up_message


@healthz_router.get('/ready')
async def ready_check() -> dict[str, str]:
    """Healthcheck для зависимостей приложения."""
    if await service.producer.check_kafka():
        return ready_message
    logger.warning('Kafka недоступна')
    raise ServerError(detail='Kafka недоступна')
