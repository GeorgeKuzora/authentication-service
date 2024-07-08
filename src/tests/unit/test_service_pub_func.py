import pytest

from app.service import AuthService, RepositoryError, User
from tests.unit.conftest import raise_repository_error, token_list, user_list


class TestRegister:
    """Тестирует метод register."""

    passwords = ['plain_password1', 'plain_password2']

    @pytest.mark.parametrize(
        'user, password, expected_token', (
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
            assert recieved_token.subject.username == expected_token.subject.username  # noqa
            assert recieved_token.subject.user_id == expected_token.subject.user_id  # noqa
            assert recieved_token.subject.password_hash == expected_token.subject.password_hash  # noqa
            assert recieved_token.issued_at == expected_token.issued_at
            assert recieved_token.encoded_token == expected_token.encoded_token

    @pytest.mark.parametrize(
        'user, expected_token, side_effect', (
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
        if expected_token is None:
            service.repository.create_user.return_value = user
            service.repository.create_token.side_effect = side_effect
        else:
            service.repository.create_user.side_effect = side_effect
            service.repository.create_token.return_value = expected_token

        with pytest.raises(RepositoryError):
            service.register(user.username, 'password')
