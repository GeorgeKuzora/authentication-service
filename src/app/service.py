import logging
from dataclasses import dataclass

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
