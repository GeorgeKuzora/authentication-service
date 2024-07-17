from collections import namedtuple

import pytest

from app.core.authentication import AuthService, Token, User
from app.core.config import get_auth_config
from app.external.in_memory_repository import InMemoryRepository


@pytest.fixture
def service():
    """
    Фикстура создает экземпляр сервиса.

    Атрибуты сервиса repository, config являются реальными объектами.

    :return: экземпляр сервиса
    :rtype: AuthService
    """
    config = get_auth_config()
    repository = InMemoryRepository()
    return AuthService(repository=repository, config=config)


TestUser = namedtuple('TestUser', 'username, password')

test_user1 = TestUser('george', 'password_1')
test_user2 = TestUser('peter', 'password_2')


class TestRegister:
    """Тестирует метод register."""

    register_fields = 'username, password'

    @pytest.mark.parametrize(
        register_fields, (
            pytest.param(
                test_user1.username,
                test_user1.password,
                id='valid user 1',
            ),
            pytest.param(
                test_user2.username,
                test_user2.password,
                id='valid user 2',
            ),
        ),
    )
    def test_register(
        self, username, password, service: AuthService,
    ):
        """Тестирует метод register."""
        token = service.register(username, password)

        if token is not None:
            assert token.subject.username == username
            assert token.encoded_token
            assert token.issued_at
            assert service.hash.validate(
                password, token.subject.password_hash,
            )
        else:
            raise AssertionError()


class TestAuthenticate:
    """Тестирует метод authenticate."""

    is_not_none = False
    is_none = True

    @pytest.fixture
    def service_db_user_yes_token_no(self, service: AuthService):
        """
        Возвращает функцию для создания сервиса.

        Возвращаемая функция примает username и password
        и создает запись о пользователе в базе данных.

        :param service: экземпляр сервиса
        :type service: AuthService
        :return: функция создания сервиса
        :rtype: callable
        """
        def _service_db_user_yes_token_no(username, password):  # noqa: WPS430, E501 need for service state parametrization
            user_id = 1
            user = User(
                username,
                service.hash.get(password),
                user_id,
            )
            service.repository.create_user(user)
            return service
        return _service_db_user_yes_token_no

    @pytest.fixture
    def service_db_user_yes_token_yes(self, service: AuthService):
        """
        Возвращает функцию для создания сервиса.

        Возвращаемая функция примает username и password,
        создает запись о пользователе в базе данных
        и добавляет токен для пользователя в базу данных.

        :param service: экземпляр сервиса
        :type service: AuthService
        :return: функция создания сервиса
        :rtype: callable
        """
        def _service_db_user_yes_token_yes(username, password):  # noqa: WPS430, E501 need for service state parametrization
            user_id = 1
            user = User(
                username,
                service.hash.get(password),
                user_id,
            )
            user = service.repository.create_user(user)
            token = service.encoder.encode(user)
            service.repository.create_token(token)
            return service
        return _service_db_user_yes_token_yes

    @pytest.fixture
    def service_db_user_not_in_db(self, service: AuthService):
        """
        Возвращает функцию для создания сервиса.

        Возвращаемая функция примает username и password.
        Возвращаемая функция создвет сервис без записей в базе данных.

        :param service: экземпляр сервиса
        :type service: AuthService
        :return: функция создания сервиса
        :rtype: callable
        """
        def _service_db_user_not_id_db(username, password):  # noqa: WPS430, E501 need for service state parametrization
            return service
        return _service_db_user_not_id_db

    @pytest.fixture
    def service_db_user_with_invalid_pass(self, service: AuthService):
        """
        Возвращает функцию для создания сервиса.

        Возвращаемая функция примает username и password,
        создает запись о пользователе в базе данных.
        При этом созданный пользователь имеет хэш пароля
        не соответствующий переданному паролю.

        :param service: экземпляр сервиса
        :type service: AuthService
        :return: функция создания сервиса
        :rtype: callable
        """
        def _service_db_user_yes_token_no(username, password):  # noqa: WPS430, E501 need for service state parametrization
            user_id = 1
            invalid_password = 'invalid_password'  # noqa: S105 test pass
            user = User(
                username,
                service.hash.get(invalid_password),
                user_id,
            )
            service.repository.create_user(user)
            return service
        return _service_db_user_yes_token_no

    @pytest.mark.parametrize(
        'user, service_state_factory, token_is_none', (
            pytest.param(
                test_user1,
                'service_db_user_yes_token_no',
                is_not_none,
                id='user in db without token',
            ),
            pytest.param(
                test_user1,
                'service_db_user_yes_token_yes',
                is_not_none,
                id='user in db with token',
            ),
            pytest.param(
                test_user1,
                'service_db_user_not_in_db',
                is_none,
                id='user not in db',
            ),
            pytest.param(
                test_user1,
                'service_db_user_with_invalid_pass',
                is_none,
                id='user has invalid password',
            ),
        ),
    )
    def test_authenticate(
        self,
        user,
        service_state_factory,
        token_is_none,
        request,
    ):
        """Тестирует метод authenticate."""
        factory = request.getfixturevalue(service_state_factory)
        srv: AuthService = factory(user.username, user.password)

        token: Token | None = srv.authenticate(
            user.username, user.password,
        )

        if token_is_none:
            assert token is None
        else:
            assert token is not None
            assert srv.hash.validate(
                user.password, token.subject.password_hash,
            )
            assert token.subject.username == user.username
