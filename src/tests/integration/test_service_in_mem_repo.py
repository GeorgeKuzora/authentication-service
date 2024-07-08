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


class TestRegister:
    """Тестирует метод register."""

    @pytest.mark.parametrize(
        'username, password', (
            pytest.param(
                usenames_and_passwords[0]['username'],
                usenames_and_passwords[0]['password'],
                id='valid user 1',
            ),
            pytest.param(
                usenames_and_passwords[1]['username'],
                usenames_and_passwords[1]['password'],
                id='valid user 2',
            ),
        ),
    )
    def test_register(
        self, username, password, service: AuthService,  # noqa
    ):
        """Тестирует метод register."""
        token = service.register(username, password)

        if token is not None:
            assert token.subject.username == username
            assert token.encoded_token
            assert token.issued_at
            assert service._verify_password(  # noqa
                password, token.subject.password_hash,
            )
        else:
            raise AssertionError()
