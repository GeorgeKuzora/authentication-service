import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol, Self

import jwt
from passlib.context import CryptContext

from app.core.config import AuthConfig

logger = logging.getLogger(__name__)


@dataclass
class User:
    """
    Данные о пользователе.

    Attributes:
        username: str - имя пользователя
        password_hash: str - хэш пароля пользователя
    """

    username: str
    password_hash: str
    user_id: int | None = None

    def __eq__(self, user: Self) -> bool:
        """
        Метод сравнения двух объектов.

        :param user: объект для сравнения
        :type: Self
        :return: логическое значение равны ли объекты
        :rtype: bool
        """
        return (
            self.username == user.username and
            self.password_hash == user.password_hash
        )


@dataclass
class Token:
    """
    Данные о токене.

    Attributes:
        subject: User - пользовать для которого создан токен
        issued_at: datetime - дата и время создания токена
        encoded_token: str - кодированное представление токена
    """

    subject: User
    issued_at: datetime
    encoded_token: str
    token_id: int | None = None

    def __eq__(self, token: Self) -> bool:
        """
        Метод сравнения двух объектов.

        :param token: объект для сравнения
        :type: Self
        :return: логическое значение равны ли объекты
        :rtype: bool
        """
        return (
            self.subject == token.subject and
            self.issued_at == token.issued_at and
            self.encoded_token == token.encoded_token
        )


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
            subject=user, issued_at=issued_at, encoded_token=encoded_token,
        )


class AuthService:
    """
    Сервис аутентификации пользователя.

    Сервис позволяет проводить регистрацию и аутентификацию
    пользоватей. Создает JWT токен.

    Attributes:
        repository: Repository - хранилище данных.
        _token_encoding_algotithm: str - алгоритм кодирования токена.
        _secret_key: str - ключ для кодирования токена.
        _pwd_context: CryptContext - контекст для хэширования пароля.
    """

    def __init__(self, repository: Repository, config: AuthConfig) -> None:
        """
        Функция инициализации.

        :param repository: хранилище данных.
        :type repository: Repository
        :param config: данные конфигурации сервиса
        :type config: AuthConfig
        """
        self.repository = repository
        self.encoder = JWTEncoder(config)
        self.hash = Hash()

    def register(self, username: str, password: str) -> Token | None:
        """
        Регистрирует пользователя и возвращает токен.

        Регистрирует и сохраняет пользователя в базе данных.
        Создает и возвращает токен для зарегистрированного пользователя.

        :param username: имя пользователя.
        :type username: str
        :param password: пароль пользователя.
        :type password: str
        :return: JWT токен пользователя.
        :rtype: Token, None
        """
        password_hash = self.hash.get(password)
        user = User(username=username, password_hash=password_hash)
        user = self.repository.create_user(user)
        token = self.encoder.encode(user)
        return self.repository.create_token(token)

    def authenticate(self, username: str, password: str) -> Token | None:
        """
        Аутентифицирует пользователя и возвращает токен.

        Аутентифицирует пользователя и проверяет наличие токена.
        Если токена нет создает и возвращает токен пользователя.
        Если токен есть обновляет и возвращает токен пользователя.
        Если пользователь не найден либо данные пользователя неверны,
        возвращает None.

        :param username: имя пользователя.
        :type username: str
        :param password: пароль пользователя.
        :type password: str
        :return: JWT токен пользователя.
        :rtype: Token, None
        """
        password_hash = self.hash.get(password)
        user = User(username=username, password_hash=password_hash)
        user_in_db = self.repository.get_user(user)

        if user_in_db is None:
            logger.info(f'user {username} not found in db')
            return None

        if not self.hash.validate(  # noqa: WPS337 one condition
            password, user_in_db.password_hash,
        ):
            logger.info(f'user {username} failed password verification')
            return None

        token = self.repository.get_token(user)
        if token is None:
            token = self.encoder.encode(user)
            token = self.repository.create_token(token)
        else:
            token = self.encoder.encode(user)
            token = self.repository.update_token(token)
        return token
