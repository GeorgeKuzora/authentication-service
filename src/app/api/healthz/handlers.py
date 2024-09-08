import logging

from fastapi import APIRouter, Request

from app.core.errors import ServerError

logger = logging.getLogger(__name__)

healthz_router = APIRouter(prefix='/healthz', tags=['healthz'])

up_message = {'message': 'service is up'}
ready_message = {'message': 'service is ready'}


@healthz_router.get('/up')
async def up_check() -> dict[str, str]:
    """
    Healthcheck для сервера сервиса.

    :return: Сообщение о успехе.
    :rtype: dict[str, str]
    """
    return up_message


@healthz_router.get('/ready')
async def ready_check(request: Request) -> dict[str, str]:
    """
    Healthcheck для зависимостей приложения.

    :param request: Запрос пользователя.
    :type request: Request
    :return: Сообщение о успехе.
    :rtype: dict[str, str]
    :raises ServerError: Сервис недоступен.
    """
    service = request.app.service
    if await service.producer.check_kafka():
        return ready_message
    logger.warning('Kafka недоступна')
    raise ServerError(detail='Kafka недоступна')
