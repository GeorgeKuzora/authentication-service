import logging
import os
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

import jwt
from passlib.context import CryptContext

logger = logging.getLogger(__name__)


class RepositoryError(Exception):
    """
    Исключение возникающее при запросе в хранилище данных.

    Импортировать в имплементации репозитория данных,
    для вызова исключения при ошибке доступа к данным.
    """


@dataclass
class User:
    username: str
    password_hash: str


@dataclass
class Token:
    subject: User
    issued_at: datetime
    encoded_token: str


class Repository(Protocol):
    """
    Интерфейс для работы с хранилищами данных.

    Repository - это слой абстракции для работы с хранилищами данных.
    Служит для уменьшения связности компонентов сервиса.
    """

    def create_user(self, user: User) -> User:
        """Абстрактный метод создания пользователя."""
        ...

    def create_token(self, token: Token) -> Token:
        """Абстрактный метод создания токена."""
        ...

    def get_user(self, user: User) -> User | None:
        """Абстрактный метод получения токена."""
        ...

    def get_token(self, user: User) -> Token | None:
        """Абстрактный метод получения токена."""
        ...

    def update_token(self, token: Token) -> Token:
        """Абстрактный метод обновления токена."""
        ...


class AuthService:
    def __init__(self, repository: Repository) -> None:
        self.repository = repository
        self._token_encoding_algorithm = os.environ['TOKEN_ALGORITHM']
        self._secret_key = os.environ['SECRET_KEY']
        self._pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def register(self, username: str, password: str) -> Token | None:
        password_hash = self._get_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        user = self.repository.create_user(user)
        logger.info(f'user {username} created in db')
        token = self._create_token(user)
        return token

    def _get_password_hash(self, password) -> str:
        return self._pwd_context.hash(password)

    def _create_token(self, user: User) -> Token:
        token = self._encode_token(user)
        token = self.repository.create_token(token)
        logger.info(f'token for user {user.username} created in db')
        return token

    def _encode_token(self, user: User) -> Token:
        issued_at = datetime.now()
        encoded_token: str = jwt.encode(
            payload={'sub': user.username, 'iat': issued_at},
            key=self._secret_key,
            algorithm=self._token_encoding_algorithm
        )
        return Token(
            subject=user, issued_at=issued_at, encoded_token=encoded_token
        )

    def authenticate(self, username: str, password: str) -> Token | None:
        password_hash = self._get_password_hash(password)
        user = User(username=username, password_hash=password_hash)
        user_in_db = self.repository.get_user(user)
        if user_in_db is None:
            logger.info(f'user {username} not found in db')
            return None
        if not self._verify_password(
            plain_password=password, hashed_password=user_in_db.password_hash
        ):
            logger.info(f'user {username} failed password verification')
            return None
        token = self.repository.get_token(user_in_db)
        if token is None:
            token = self._create_token(user_in_db)
        else:
            token = self._update_token(user_in_db)
        return token

    def _update_token(self, user: User) -> Token:
        token = self._encode_token(user)
        token = self.repository.update_token(token)
        logger.info(f'token for user {user.username} updated in db')
        return token

    def _verify_password(self, plain_password, hashed_password) -> bool:
        return self._pwd_context.verify(plain_password, hashed_password)
