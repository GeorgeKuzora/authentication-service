import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Any, Protocol

import jwt
from fastapi import Header, UploadFile
from passlib.context import CryptContext

from app.core.config import AuthConfig
from app.core.errors import AuthorizationError, NotFoundError
from app.core.models import Token, User, UserCredentials

logger = logging.getLogger(__name__)


class Repository(Protocol):
    """
    Интерфейс для работы с хранилищами данных.

    Repository - это слой абстракции для работы с хранилищами данных.
    Служит для уменьшения связности компонентов сервиса.
    """

    def create_user(self, user: User) -> User:
        """
        Абстрактный метод создания пользователя.

        :param user: объект пользователя
        :type user: User
        """
        ...  # noqa: WPS428 default Protocol syntax

    def create_token(self, token: Token) -> Token:
        """
        Абстрактный метод создания токена.

        :param token: объект токена
        :type token: Token
        """
        ...  # noqa: WPS428 default Protocol syntax

    def get_user(self, user: User) -> User | None:
        """
        Абстрактный метод получения токена.

        :param user: объект пользователя
        :type user: User
        """
        ...  # noqa: WPS428 default Protocol syntax

    def get_token(self, user: User) -> Token | None:
        """
        Абстрактный метод получения токена.

        :param user: объект пользователя
        :type user: User
        """
        ...  # noqa: WPS428 default Protocol syntax

    def update_token(self, token: Token) -> Token:
        """
        Абстрактный метод обновления токена.

        :param token: объект токена
        :type token: Token
        """
        ...  # noqa: WPS428 default Protocol syntax


class Cache(Protocol):
    """Интерфейс кэша сервиса."""

    async def get_cache(self, cached_value: Any) -> Any:
        """
        Получает значение из кэша.

        :param cached_value: Кэшированное значение
        :type cached_value: Any
        """
        ...  # noqa: WPS428 valid protocol syntax

    async def create_cache(self, cached_value: Any) -> None:
        """
        Записывает значение в кэш.

        :param cached_value: Кэшируемое значение
        :type cached_value: Any
        """
        ...  # noqa: WPS428 valid protocol syntax


class Queue(Protocol):
    """Интерфейс кэша сервиса."""

    async def send_message(self, username: str, image: UploadFile) -> None:
        """
        Отправляет сообщение с файлом.

        :param username: имя пользователя
        :type username: str
        :param image: изображение пользователя
        :type image: UploadFile
        """
        ...  # noqa: WPS428 valid protocol syntax


@dataclass
class Hash:
    """Класс алгоритма хэширования."""

    _pwd_context: CryptContext = CryptContext(
        schemes=['bcrypt'], deprecated='auto',
    )

    def get(self, string: str) -> str:
        """
        Метод получения хэша.

        :param string: строка для хэширования
        :type string: str
        :return: хэш переданного значения
        :rtype: str
        """
        return self._pwd_context.hash(string)

    def validate(self, string: str, hashed_str: str) -> bool:
        """
        Метод валидации хэша.

        :param string: строка для валидации.
        :type string: str
        :param hashed_str: хэш для валидации
        :type hashed_str: str
        :return: валиден ли хэш
        :rtype: bool
        """
        return self._pwd_context.verify(string, hashed_str)


class JWTEncoder:
    """Алгоритм шифрования JWT токена."""

    def __init__(self, config: AuthConfig) -> None:
        """
        Метод инициализации.

        :param config: конфигурация алгоритма
        :type config: AuthConfig
        """
        self.config = config

    def encode(self, user: User) -> Token:
        """
        Метод кодирования токена.

        :param user: пользователь владелец токена
        :type user: User
        :return: токен пользователя
        :rtype: Token
        """
        issued_at = datetime.now()
        encoded_token: str = jwt.encode(
            payload={'sub': user.username, 'iat': issued_at},
            key=self.config.secret_key,
            algorithm=self.config.algorithm,
        )
        return Token(
            subject=user.username,
            issued_at=issued_at,
            encoded_token=encoded_token,
        )

    def decode(self, encoded_token: str) -> Token:
        """
        Метод декодирования токена.

        :param encoded_token: jwt токен в закодированом виде
        :type encoded_token: str
        :return: токен пользователя
        :rtype: Token
        """
        decoded_token = jwt.decode(
            jwt=encoded_token,
            key=self.config.secret_key,
            algorithm=self.config.algorithm,
        )
        return Token(
            subject=decoded_token.get('sub'),
            issued_at=decoded_token.get('iat'),
            encoded_token=encoded_token,
        )


class AuthService:
    """
    Сервис аутентификации пользователя.

    Сервис позволяет проводить регистрацию и аутентификацию
    пользоватей. Создает JWT токен.
    """

    def __init__(
        self,
        repository: Repository,
        config: AuthConfig,
        cache: Cache,
        queue: Queue,
    ) -> None:
        """
        Функция инициализации.

        :param repository: хранилище данных.
        :type repository: Repository
        :param config: данные конфигурации сервиса
        :type config: AuthConfig
        :param cache: Кэш сервиса
        :type cache: Cache
        :param queue: Очередь сообщений сервиса
        :type queue: Queue
        """
        self.repository = repository
        self.encoder = JWTEncoder(config)
        self.hash = Hash()
        self.cache = cache
        self.queue = queue

    async def register(self, user_creds: UserCredentials) -> Token:
        """
        Регистрирует пользователя и возвращает токен.

        Регистрирует и сохраняет пользователя в базе данных.
        Создает и возвращает токен для зарегистрированного пользователя.

        :param user_creds: Данные пользователя
        :type user_creds: UserCredentials
        :return: JWT токен пользователя.
        :rtype: Token, None
        """
        password_hash = self.hash.get(user_creds.password)
        user = User(username=user_creds.username, password_hash=password_hash)
        user = self.repository.create_user(user)
        token = self.encoder.encode(user)
        await self.cache.create_cache(token)
        return token

    async def authenticate(
        self,
        user_creds: UserCredentials,
        authorization: Annotated[str, Header()],
    ) -> Token:
        """
        Аутентифицирует пользователя и возвращает токен.

        Аутентифицирует пользователя и проверяет наличие токена.

        :param user_creds: Данные пользователя
        :type user_creds: UserCredentials
        :param authorization: Заголовок авторизации
        :type authorization: Annotated[str, Header()
        :return: JWT токен пользователя.
        :rtype: Token, None
        :raises NotFoundError: Если пользователь не найден
        :raises AuthorizationError: При провале авторизации
        """
        password_hash = self.hash.get(user_creds.password)
        user = User(username=user_creds.username, password_hash=password_hash)
        user_in_db = self.repository.get_user(user)

        if user_in_db is None:
            logger.info(f'user {user_creds.username} not found in db')
            raise NotFoundError(f'user {user_creds.username} not found in db')

        if not self.hash.validate(  # noqa: WPS337 one condition
            user_creds.password, user_in_db.password_hash,
        ):
            logger.info(
                f'user {user_creds.username} failed password verification',
            )
            raise AuthorizationError(
                f'user {user_creds.username} failed password verification',
            )

        token_value = authorization.split(maxsplit=1)[1]
        token_value_decoded = self.encoder.decode(token_value)
        try:
            token = await self.cache.get_cache(token_value_decoded)
        except KeyError:
            logger.info(f'token cache not found for user {user}')
            token = None

        if token is None or token.is_expired():
            token = self.encoder.encode(user)
            await self.cache.create_cache(token)
        return token

    async def check_token(
        self, authorization: Annotated[str, Header()],
    ) -> dict[str, str]:
        """
        Валидирует токен пользователя.

        :param authorization: Заголовок авторизации
        :type authorization: Annotated[str, Header()
        :return: Сообщение об успехе.
        :rtype: dict[str, str]
        :raises NotFoundError: Токен не найден
        :raises AuthorizationError: Срок действия токена вышел
        """
        token_value = authorization.split(maxsplit=1)[1]
        token_value_decoded = self.encoder.decode(token_value)
        try:
            token: Token = await self.cache.get_cache(token_value_decoded)
        except KeyError:
            logger.info(
                f'token cache not found for user {token_value_decoded.subject}',
            )
            raise NotFoundError(
                f'token cache not found for user {token_value_decoded.subject}',
            )

        if token.is_expired():
            logger.info(
                f'token is expired for user {token.subject}',
            )
            raise AuthorizationError(
                f'token is expired for user {token.subject}',
            )
        return {'message': 'ok'}

    async def verify(
        self, user_creds: UserCredentials, image: UploadFile,
    ) -> None:
        """
        Верифицирует пользователя.

        Отправляет сообщение с именим пользователя и изображением
        пользователя в очередь сообщений.

        :param user_creds: Данные пользователя
        :type user_creds: UserCredentials
        :param image: изображение пользователя
        :type image: UploadFile
        :return: Сообщение об успехе.
        :rtype: dict[str, str]
        """
        await self.queue.send_message(user_creds.username, image)
