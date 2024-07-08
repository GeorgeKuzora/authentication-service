import pytest

from app.config import get_auth_config
from app.in_memory_repository import InMemoryRepository
from app.service import AuthService, Token, User


@pytest.fixture
def service():
    """
    Фикстура создает экземпляр сервиса.

    Атрибуты сервиса repository, config являются реальными объектами.
    """
    config = get_auth_config()
    repository = InMemoryRepository()
    return AuthService(repository=repository, config=config)


usenames_and_passwords = [
    {'username': 'george', 'password': 'password_1'},
    {'username': 'peter', 'password': 'password_2'},
]
