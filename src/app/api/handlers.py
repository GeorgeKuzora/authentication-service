import asyncio
import logging
from typing import Annotated

from fastapi import BackgroundTasks, Header, HTTPException, UploadFile, status

from app.core.authentication import AuthService
from app.core.config import get_auth_config
from app.core.errors import AuthorizationError, NotFoundError
from app.core.models import Token, UserCredentials
from app.external.in_memory_repository import InMemoryRepository
from app.external.kafka import KafkaQueue
from app.external.redis import TokenCache
from app.service import app

logger = logging.getLogger(__name__)


def get_service() -> AuthService:
    """Инициализирует сервис."""
    cache = TokenCache()
    persistent = InMemoryRepository()
    config = get_auth_config()
    queue = KafkaQueue()
    return AuthService(
        repository=persistent, cache=cache, config=config, queue=queue,
    )


async def authenticate(
    user_creds: UserCredentials,
    authorization: Annotated[str, Header()],
) -> Token:
    """Хэндлер аутентификации пользователя."""
    service = get_service()
    task = asyncio.create_task(service.authenticate(user_creds, authorization))
    try:
        return await task
    except NotFoundError as not_found_err:
        logger.info(f'{user_creds.username} not found')
        raise HTTPException(
            status_code=status.HTTP_404,
            detail=f'{user_creds.username} not found',
        ) from not_found_err
    except AuthorizationError as auth_err:
        logger.info(f'{user_creds.username} unauthorized')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'{user_creds.username} unauthorized',
        ) from auth_err
    except Exception as err:
        logger.info('server error in /authenticate')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from err


@app.post('/register')  # type: ignore
async def register(user_creds: UserCredentials) -> Token:
    """Хэндлер регистрации пользователя."""
    service = get_service()
    task = asyncio.create_task(service.register(user_creds))
    try:
        return await task
    except Exception as err:
        logger.error('unexpected server error in /register')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from err


@app.post('/check_token')  # type: ignore
async def check_token(
    authorization: Annotated[str, Header()],
) -> dict[str, str]:
    """Хэндлер валидации токена пользователя."""
    service = get_service()
    task = asyncio.create_task(service.check_token(authorization))
    try:
        return await task  # type: ignore
    except NotFoundError as not_found_err:
        logger.info('token not found error in /check_token')
        raise HTTPException(
            status_code=status.HTTP_404,
        ) from not_found_err
    except AuthorizationError as auth_err:
        logger.info('authorisation error in /check_token')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from auth_err
    except Exception as err:
        logger.error('server error in /check_token')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from err


@app.post('/verify')  # type: ignore
async def verify(
    user_creds: UserCredentials,
    image: UploadFile,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Верифицирует пользователя."""
    service = get_service()
    background_tasks.add_task(
        service.verify, user_creds=user_creds, image=image,
    )
    return {'message': 'ok'}
