import pytest

from app.core.authentication import AuthService, Token, User
from app.core.config import get_auth_config
from app.external.in_memory_repository import InMemoryRepository


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


class TestAuthenticate:
    """Тестирует метод authenticate."""

    is_not_none = False
    is_none = True

    @pytest.fixture
    def service_db_user_yes_token_no(self, service: AuthService):  # noqa
        """
        Возвращает функцию для создания сервиса.

        Возвращаемая функция примает username и password
        и создает запись о пользователе в базе данных.
        """
        def _service_db_user_yes_token_no(username, password):
            user_id = 1
            user = User(
                username,
                service._get_password_hash(password),  # noqa
                user_id,
            )
            service.repository.create_user(user)
            return service
        yield _service_db_user_yes_token_no

    @pytest.fixture
    def service_db_user_yes_token_yes(self, service: AuthService):  # noqa
        """
        Возвращает функцию для создания сервиса.

        Возвращаемая функция примает username и password,
        создает запись о пользователе в базе данных
        и добавляет токен для пользователя в базу данных.
        """
        def _service_db_user_yes_token_yes(username, password):
            user_id = 1
            user = User(
                username,
                service._get_password_hash(password),  # noqa
                user_id,
            )
            service.repository.create_user(user)
            service._create_token(user)  # noqa
            return service
        yield _service_db_user_yes_token_yes

    @pytest.fixture
    def service_db_user_not_in_db(self, service: AuthService):  # noqa
        """
        Возвращает функцию для создания сервиса.

        Возвращаемая функция примает username и password.
        Возвращаемая функция создвет сервис без записей в базе данных.
        """
        def _service_db_user_not_id_db(username, password):
            return service
        yield _service_db_user_not_id_db

    @pytest.fixture
    def service_db_user_with_invalid_pass(self, service: AuthService):  # noqa
        """
        Возвращает функцию для создания сервиса.

        Возвращаемая функция примает username и password,
        создает запись о пользователе в базе данных.
        При этом созданный пользователь имеет хэш пароля
        не соответствующий переданному паролю.
        """
        def _service_db_user_yes_token_no(username, password):
            user_id = 1
            invalid_password = 'invalid_password'
            user = User(
                username,
                service._get_password_hash(invalid_password),  # noqa
                user_id,
            )
            service.repository.create_user(user)
            return service
        yield _service_db_user_yes_token_no

    @pytest.mark.parametrize(
        'username, password, service_state_factory, token_is_none', (
            pytest.param(
                usenames_and_passwords[0]['username'],
                usenames_and_passwords[0]['password'],
                'service_db_user_yes_token_no',
                is_not_none,
                id='user in db without token',
            ),
            pytest.param(
                usenames_and_passwords[0]['username'],
                usenames_and_passwords[0]['password'],
                'service_db_user_yes_token_yes',
                is_not_none,
                id='user in db with token',
            ),
            pytest.param(
                usenames_and_passwords[0]['username'],
                usenames_and_passwords[0]['password'],
                'service_db_user_not_in_db',
                is_none,
                id='user not in db',
            ),
            pytest.param(
                usenames_and_passwords[0]['username'],
                usenames_and_passwords[0]['password'],
                'service_db_user_with_invalid_pass',
                is_none,
                id='user has invalid password',
            ),
        ),
    )
    def test_authenticate(  # noqa
        self,
        username,
        password,
        service_state_factory,
        token_is_none,
        request,
    ):
        """Тестирует метод authenticate."""
        factory = request.getfixturevalue(service_state_factory)
        srv: AuthService = factory(username, password)

        token: Token | None = srv.authenticate(username, password)

        if token_is_none:
            assert token is None
        else:
            assert token is not None
            assert token.subject.username == username
            assert srv._verify_password(  # noqa
                password, token.subject.password_hash,
            )
            assert token.encoded_token
            assert token.issued_at
