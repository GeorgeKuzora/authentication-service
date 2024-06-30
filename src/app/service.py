import logging
from dataclasses import dataclass
from typing import Protocol

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
