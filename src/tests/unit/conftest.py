from datetime import datetime
from unittest.mock import MagicMock

import pytest

from app.core.authentication import AuthService, RepositoryError, Token, User
from app.external.in_memory_repository import InMemoryRepository

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
invalid_user = User('invalid', 'invalid')
invalid_token = Token(invalid_user, datetime.now(), 'sdfa')


@pytest.fixture
def service():
    """
    Фикстура создает экземпляр сервиса.

    Атрибуты сервиса repository, config являются mock объектами.
    """
    repository = MagicMock()
    config = MagicMock()
    config.token_algorithm = 'HS256'
    config.secret_key = '09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b89e8d3e7'  # noqa

    return AuthService(repository=repository, config=config)


@pytest.fixture
def repository():
    """Фикстура для создания объекта InMemoryRepository."""
    return InMemoryRepository()


def raise_repository_error(*args, **kwargs):
    """Функция для вызова RepositoryError."""
    raise RepositoryError


@pytest.fixture
def single_user_in_repo_facrory(repository):  # noqa
    """Фикстура репозитория с одной записью о пользователе."""
    users_in_repo = 1
    repository.create_user(user_list[0])
    return repository, users_in_repo


@pytest.fixture
def two_users_in_repo_facrory(repository):  # noqa
    """Фикстура репозитория с двумя записями о пользователях."""
    users_in_repo = 2
    for user_id in range(users_in_repo):
        repository.create_user(user_list[user_id])
    return repository, users_in_repo


@pytest.fixture
def single_token_in_repo_facrory(repository):  # noqa
    """Фикстура репозитория с одной записью о токене."""
    tokens_in_repo = 1
    repository.create_token(token_list[0])
    return repository, tokens_in_repo


@pytest.fixture
def two_tokens_in_repo_facrory(repository):  # noqa
    """Фикстура репозитория с двумя записями о токенах."""
    tokens_in_repo = 2
    for token_id in range(tokens_in_repo):
        repository.create_token(token_list[token_id])
    return repository, tokens_in_repo
