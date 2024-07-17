import pytest

from app.core.authentication import AuthService, User
from app.core.errors import RepositoryError
from tests.unit.conftest import raise_repository_error, token_list, user_list

param_fields = 'user, password, expected_token'
param_fields_with_side_effect = 'user, expected_token, side_effect'


class TestRegister:
    """Тестирует метод register."""

    passwords = ['plain_password1', 'plain_password2']

    @pytest.mark.parametrize(
        param_fields, (
            pytest.param(
                user_list[0],
                passwords[0],
                token_list[0],
                id='valid user 1',
            ),
            pytest.param(
                user_list[1],
                passwords[1],
                token_list[1],
                id='valid user 2',
            ),
            pytest.param(
                user_list[1],
                passwords[1],
                None,
                id='repository returned None',
            ),
        ),
    )
    def test_register(self, user, password, expected_token, service):
        """Тестирует позитивные сценарии."""
        service.repository.create_token.return_value = expected_token
        service.repository.create_user.return_value = user

        recieved_token = service.register(user.username, password)

        assert isinstance(recieved_token, type(expected_token))
        if recieved_token is not None:
            assert recieved_token == expected_token

    @pytest.mark.parametrize(
        param_fields_with_side_effect, (
            pytest.param(
                user_list[0],
                None,
                raise_repository_error,
                id='error in repository',
            ),
            pytest.param(
                user_list[0],
                token_list[0],
                raise_repository_error,
                id='error in repository',
            ),
        ),
    )
    def test_register_raises(
        self, user: User, expected_token, side_effect, service: AuthService,
    ):
        """Тестирует негативные сценарии."""
        password = 'password'  # noqa: S105 test password
        if expected_token is None:
            service.repository.create_user.return_value = user
            service.repository.create_token.side_effect = side_effect
        else:
            service.repository.create_user.side_effect = side_effect
            service.repository.create_token.return_value = expected_token

        with pytest.raises(RepositoryError):
            service.register(user.username, password)


class TestAuthenticate:
    """Тестирует метод authenticate."""

    passwords = ['plain_password1', 'plain_password2']

    @pytest.mark.parametrize(
        param_fields, (
            pytest.param(
                user_list[0],
                passwords[0],
                token_list[0],
                id='update token',
            ),
        ),
    )
    def test_authenticate_token_update(
        self, user: User, password, expected_token, service: AuthService,
    ):
        """Тестирует сценарий пользователь и токен пользователя найдены."""
        password_hash = service.hash.get(password)
        user.password_hash = password_hash
        service.repository.get_user.return_value = user
        service.repository.get_token.return_value = expected_token
        service.repository.update_token.return_value = expected_token

        recieved_token = service.authenticate(user.username, password)

        assert isinstance(recieved_token, type(expected_token))
        if recieved_token is not None:
            assert recieved_token == expected_token
        else:
            raise AssertionError()

    @pytest.mark.parametrize(
        param_fields, (
            pytest.param(
                user_list[0],
                passwords[0],
                token_list[0],
                id='create token',
            ),
        ),
    )
    def test_authenticate_token_create(
        self, user: User, password, expected_token, service: AuthService,
    ):
        """Тестирует сценарий токен пользователя не найден."""
        password_hash = service.hash.get(password)
        user.password_hash = password_hash
        service.repository.get_user.return_value = user
        service.repository.get_token.return_value = None
        service.repository.create_token.return_value = expected_token

        recieved_token = service.authenticate(user.username, password)

        assert isinstance(recieved_token, type(expected_token))
        if recieved_token is not None:
            assert recieved_token == expected_token
        else:
            raise AssertionError()

    @pytest.mark.parametrize(
        param_fields, (
            pytest.param(
                user_list[0],
                passwords[0],
                token_list[0],
                id='user not found token is None',
            ),
        ),
    )
    def test_authenticate_user_not_found(
        self, user: User, password, expected_token, service: AuthService,
    ):
        """Тестирует сценарий пользователь не найден."""
        password_hash = service.hash.get(password)
        user.password_hash = password_hash
        service.repository.get_user.return_value = None
        service.repository.get_token.return_value = expected_token
        service.repository.create_token.return_value = expected_token

        recieved_token = service.authenticate(user.username, password)

        assert recieved_token is None

    @pytest.mark.parametrize(
        param_fields, (
            pytest.param(
                user_list[0],
                passwords[0],
                token_list[0],
                id='not veirfied token is None',
            ),
        ),
    )
    def test_authenticate_user_not_verified(
        self, user: User, password, expected_token, service: AuthService,
    ):
        """Тестирует сценарий пользователь не найден."""
        password_hash = service.hash.get(password)
        user.password_hash = password_hash
        invalid_password = 'invalid_password'  # noqa: S105 invalid pass

        service.repository.get_user.return_value = user
        service.repository.get_token.return_value = expected_token
        service.repository.create_token.return_value = expected_token

        recieved_token = service.authenticate(user.username, invalid_password)

        assert recieved_token is None

    @pytest.mark.parametrize(
        'user, password', (
            pytest.param(
                user_list[0],
                passwords[0],
                id='raises RepositoryError',
            ),
        ),
    )
    def test_authenticate_raises(
        self, user: User, password, service: AuthService,
    ):
        """Тестирует возврат ошибки при ошибке в репозитории."""
        password_hash = service.hash.get(password)
        user.password_hash = password_hash

        service.repository.get_user.side_effect = raise_repository_error
        service.repository.get_token.side_effect = raise_repository_error
        service.repository.create_token.side_effect = raise_repository_error

        with pytest.raises(RepositoryError):
            service.authenticate(user.username, password)
