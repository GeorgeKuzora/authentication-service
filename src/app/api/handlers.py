import asyncio
from fastapi import FastAPI, Header, status, HTTPException, UploadFile, BackgroundTasks
from pydantic import ValidationError
from typing import Annotated
import logging
from app.core.authentication import AuthService
from app.core.models import Token, UserCredentials
from app.core.config import get_auth_config
from app.external.in_memory_repository import InMemoryRepository
from app.external.redis import TokenCache
from app.core.errors import NotFoundError, AuthorizationError
from app.external.kafka import KafkaQueue

logger = logging.getLogger(__name__)

app = FastAPI()


def get_service() -> AuthService:
    """Инициализирует сервис."""
    cache = TokenCache()
    persistent = InMemoryRepository()
    config = get_auth_config()
    queue = KafkaQueue()
    return AuthService(
        repository=persistent, cache=cache, config=config, queue=queue,
    )


@app.post('/auth')
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
        logger.info(f'user {user_creds.username} not found')
        raise HTTPException(
            status_code=status.HTTP_404,
            detail=f'user {user_creds.username} not found',
        ) from not_found_err
    except AuthorizationError as auth_err:
        logger.info(f'user {user_creds.username} unauthorized')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'user {user_creds.username} unauthorized',
        ) from auth_err
    except Exception as err:
        logger.info('server error')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='server error',
        ) from err


@app.post('/register')
async def register(user_creds: UserCredentials) -> Token:
    """Хэндлер регистрации пользователя."""
    service = get_service()
    task = asyncio.create_task(service.register(user_creds))
    try:
        return await task
    except Exception as err:
        logger.info('unexpected server error')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='unexpected server error',
        ) from err


@app.post('/check_token')
async def check_token(
    self, authorization: Annotated[str, Header()],
) -> dict[str, str]:
    """Хэндлер валидации токена пользователя."""
    service = get_service()
    task = asyncio.create_task(service.check_token(authorization))
    try:
        return await task
    except NotFoundError as not_found_err:
        logger.info('token not found')
        raise HTTPException(
            status_code=status.HTTP_404,
            detail='token not found',
        ) from not_found_err
    except AuthorizationError as auth_err:
        logger.info('token expired')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='token expired',
        ) from auth_err
    except Exception as err:
        logger.info('server error')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='server error',
        ) from err


@app.post('/verify')
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
