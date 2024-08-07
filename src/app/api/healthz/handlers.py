import logging

from fastapi import APIRouter

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
    return ready_message
