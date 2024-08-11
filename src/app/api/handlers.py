import asyncio
import logging
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Header,
    HTTPException,
    UploadFile,
    status,
    Form,
)
from pydantic import ValidationError

from app.core.authentication import AuthService
from app.core.config import get_auth_config
from app.core.errors import AuthorizationError, NotFoundError, ServerError
from app.core.models import Token, UserCredentials, validation_rules
from app.external.in_memory_repository import InMemoryRepository
from app.external.kafka import KafkaProducer
from app.external.redis import TokenCache

logger = logging.getLogger(__name__)

router = APIRouter()


def get_service() -> AuthService:
    """Инициализирует сервис."""
    cache = TokenCache()
    persistent = InMemoryRepository()
    config = get_auth_config()
    queue = KafkaProducer()
    return AuthService(
        repository=persistent, cache=cache, config=config, producer=queue,
    )


service = get_service()


@router.post('/login')
async def authenticate(
    user_creds: UserCredentials,
    authorization: Annotated[str, Header()],
) -> Token:
    """Хэндлер аутентификации пользователя."""
    task = asyncio.create_task(service.authenticate(user_creds, authorization))
    try:
        return await task
    except NotFoundError as not_found_err:
        logger.info(f'{user_creds.username} not found')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{user_creds.username} not found',
        ) from not_found_err
    except AuthorizationError as auth_err:
        logger.info(f'{user_creds.username} unauthorized')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f'{user_creds.username} unauthorized',
        ) from auth_err
    except ServerError as err:
        logger.info('server error in /login')
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from err


@router.post('/register')
async def register(user_creds: UserCredentials) -> Token:
    """Хэндлер регистрации пользователя."""
    task = asyncio.create_task(service.register(user_creds))
    try:
        return await task
    except ValidationError as err:
        logger.error(f'Unprocessable entry {user_creds}')
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        ) from err
    except Exception as err:
        logger.error('unexpected server error in /register')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        ) from err


@router.post('/check_token')
async def check_token(
    authorization: Annotated[str, Header()],
) -> dict[str, str]:
    """Хэндлер валидации токена пользователя."""
    task = asyncio.create_task(service.check_token(authorization))
    try:
        return await task  # type: ignore
    except NotFoundError as not_found_err:
        logger.info('token not found error in /check_token')
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        ) from not_found_err
    except AuthorizationError as auth_err:
        logger.info('authorisation error in /check_token')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
        ) from auth_err
    except ServerError as err:
        logger.error('server error in /check_token')
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        ) from err


@router.post('/verify')
async def verify(
    username: Annotated[str, Form(max_length=validation_rules.username_max_len)],  # noqa: E501 can't shorten hint
    image: UploadFile,
    background_tasks: BackgroundTasks,
) -> dict[str, str]:
    """Верифицирует пользователя."""
    background_tasks.add_task(
        service.verify, username=username, image=image,
    )
    return {'message': 'ok'}
