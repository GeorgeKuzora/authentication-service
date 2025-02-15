import asyncio
import logging
from copy import deepcopy
from typing import Annotated

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Form,
    Header,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from opentracing import global_tracer
from pydantic import ValidationError

from app.core.errors import AuthorizationError, NotFoundError, ServerError
from app.core.models import Token, UserCredentials, validation_rules
from app.metrics.tracing import Tag

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post('/login')
async def authenticate(
    user_creds: UserCredentials,
    authorization: Annotated[str, Header()],
    request: Request,
) -> Token:
    """
    Хэндлер аутентификации пользователя.

    Аутентифицирует пользователя в системе.

    :param user_creds: Данные аутентификации пользователя.
    :type user_creds: UserCredentials
    :param authorization: Токен авторизации пользователя.
    :type authorization: str
    :param request: Объект запроса.
    :type request: Request
    :return: Токен авторизации пользователя.
    :rtype: Token
    :raises HTTPException: При ошибке в ходе аутентификации.
    """
    with global_tracer().start_active_span('login') as scope:
        scope.span.set_tag(Tag.username, user_creds.username)
        service = request.app.service
        task = asyncio.create_task(
            service.authenticate(user_creds, authorization),
        )
        try:
            return await task
        except NotFoundError as not_found_err:
            logger.info(f'{user_creds.username} not found')
            scope.span.set_tag(Tag.warning, 'user not found')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'{user_creds.username} not found',
            ) from not_found_err
        except AuthorizationError as auth_err:
            logger.info(f'{user_creds.username} unauthorized')
            scope.span.set_tag(Tag.warning, 'authentication failed')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f'{user_creds.username} unauthorized',
            ) from auth_err
        except ServerError as err:
            logger.info('server error in /login')
            scope.span.set_tag(Tag.error, 'unexpected error on login')
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ) from err


@router.post('/register')
async def register(user_creds: UserCredentials, request: Request) -> Token:
    """
    Хэндлер регистрации пользователя.

    Регистрирует пользователя в системе.

    :param user_creds: Данные регистрации пользователя.
    :type user_creds: UserCredentials
    :param request: Объект запроса пользователя.
    :type request: Request
    :return: Токен авторизации.
    :rtype: Token
    :raises HTTPException: При ошибке в ходе авторизации.
    """
    with global_tracer().start_active_span('register') as scope:
        scope.span.set_tag(Tag.username, user_creds.username)
        service = request.app.service
        task = asyncio.create_task(service.register(user_creds))
        try:
            return await task
        except ValidationError as err:
            logger.error(f'Unprocessable entry {user_creds}')
            scope.span.set_tag(Tag.error, "request can't be processed")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            ) from err
        except Exception as err:
            logger.error('unexpected server error in /register')
            scope.span.set_tag(Tag.error, 'unexpected error on register')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            ) from err


@router.post('/check_token')
async def check_token(
    authorization: Annotated[str, Header()], request: Request,
) -> dict[str, str]:
    """
    Хэндлер валидации токена пользователя.

    Валидирует токен авторизации пользователя.

    :param authorization: Токен авторизации пользователя.
    :type authorization: str
    :param request: Объект запроса пользователя.
    :type request: Request
    :return: Сообщение о успехе операции.
    :rtype: dict[str, str]
    :raises HTTPException: При ошибке в ходе операции.
    """
    with global_tracer().start_active_span('register') as scope:
        scope.span.set_tag(Tag.token, authorization)
        service = request.app.service
        task = asyncio.create_task(service.check_token(authorization))
        try:
            return await task  # type: ignore
        except NotFoundError as not_found_err:
            logger.info('token not found error in /check_token')
            scope.span.set_tag(Tag.warning, 'token not found')
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
            ) from not_found_err
        except AuthorizationError as auth_err:
            logger.info('authorization error in /check_token')
            scope.span.set_tag(Tag.warning, 'invalid token')
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            ) from auth_err
        except ServerError as err:
            logger.error('server error in /check_token')
            scope.span.set_tag(Tag.error, 'unexpected error on check_token')
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            ) from err


@router.post('/verify')
async def verify(
    username: Annotated[str, Form(max_length=validation_rules.username_max_len)],  # noqa: E501 can't shorten hint
    image: UploadFile,
    background_tasks: BackgroundTasks,
    request: Request,
) -> dict[str, str]:
    """
    Верифицирует пользователя.

    Загружает фотографию пользователя и передает путь к файлу
    через сообщение kafka.

    :param username: Имя пользователя.
    :type username: str
    :param image: Загружаемый пользователем файл.
    :type image: UploadFile
    :param background_tasks: Задачи для запуска в бэкграунде.
    :type background_tasks: BackgroundTasks
    :param request: Объект запроса пользователя.
    :type request: Request
    :return: Сообщение о успехе операции
    :rtype: dict[str, str]
    """
    with global_tracer().start_active_span('verify') as scope:
        scope.span.set_tag(Tag.username, username)
        service = request.app.service
        background_tasks.add_task(
            service.verify, username=username, image=deepcopy(image),
        )
        return {'message': 'ok'}
