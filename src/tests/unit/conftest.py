from datetime import datetime

import pytest
from unittest.mock import AsyncMock

from app.core.authentication import AuthService, Token, User
from app.core.errors import RepositoryError
from app.external.in_memory_repository import InMemoryRepository

issued_at = datetime.now()
encoded_token = 'sdfa.asfsd.safd'  # noqa: S105 test encoded token
user_list = [
    User(username='peter', password_hash='13rasf', user_id=1),  # noqa: S106, E501 tests
    User(username='max', password_hash='sdfad', user_id=2),  # noqa: S106, E501 tests
]
token_list = [
    Token(
        subject='peter',
        issued_at=issued_at,
        encoded_token=encoded_token,
        token_id=1,
    ),
    Token(
        subject='max',
        issued_at=issued_at,
        encoded_token=encoded_token,
        token_id=2,
    ),
]
invalid_user = User(username='invalid', password_hash='invalid')  # noqa: S106, E501 tests
invalid_token = Token(  # noqa: S106 tests
    subject='invalid', issued_at=datetime.now(), encoded_token='sdfa',
)


@pytest.fixture
def service():
    """
    Фикстура создает экземпляр сервиса.

    Атрибуты сервиса repository, config являются mock объектами.

    :return: экземпляр сервиса
    :rtype: AuthService
    """
    repository = AsyncMock()
    config = AsyncMock()
    cache = AsyncMock()
    queue = AsyncMock()

    return AuthService(
        repository=repository, config=config, cache=cache, queue=queue,
    )


@pytest.fixture
def repository():
    """Фикстура для создания объекта InMemoryRepository."""
    return InMemoryRepository()


def raise_repository_error(*args, **kwargs):
    """Функция для вызова RepositoryError."""
    raise RepositoryError


@pytest.mark.asyncio
@pytest.fixture
async def single_user_in_repo_facrory(repository):
    """Фикстура репозитория с одной записью о пользователе."""
    users_in_repo = 1
    await repository.create_user(user_list[0])
    return repository, users_in_repo


@pytest.mark.asyncio
@pytest.fixture
async def two_users_in_repo_facrory(repository):
    """Фикстура репозитория с двумя записями о пользователях."""
    users_in_repo = 2
    for user_id in range(users_in_repo):
        await repository.create_user(user_list[user_id])
    return repository, users_in_repo


@pytest.mark.asyncio
@pytest.fixture
async def single_token_in_repo_facrory(repository):
    """Фикстура репозитория с одной записью о токене."""
    tokens_in_repo = 1
    await repository.create_token(token_list[0])
    return repository, tokens_in_repo


@pytest.mark.asyncio
@pytest.fixture
async def two_tokens_in_repo_facrory(repository):
    """Фикстура репозитория с двумя записями о токенах."""
    tokens_in_repo = 2
    for token_id in range(tokens_in_repo):
        await repository.create_token(token_list[token_id])
    return repository, tokens_in_repo
