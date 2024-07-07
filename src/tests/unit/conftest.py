from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.service import AuthService, RepositoryError, Token, User

issued_at = datetime.now()
encoded_token = 'sdfa.asfsd.safd'
user_list = [
    User('peter', '13rasf', 1),
    User('max', 'sdfad', 2),
]
token_list = [
    Token(user_list[0], issued_at, encoded_token, 1),
    Token(user_list[1], issued_at, encoded_token, 2),
]


@pytest.fixture
def service():
    """
    Фикстура создает экземляр сервиса.

    Атрибуты сервиса repository, config являются mock объектами.
    """
    repository = MagicMock()
    config = MagicMock()
    config.token_algorithm = 'HS256'
    config.secret_key = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b89e8d3e7'  # noqa

    return AuthService(repository=repository, config=config)


def raise_repository_error(*args, **kwargs):
    """Функция для вызова RepositoryError."""
    raise RepositoryError
