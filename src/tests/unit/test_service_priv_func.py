import pytest

from app.service import AuthService, RepositoryError, Token, User
from tests.unit.conftest import raise_repository_error, token_list, user_list


class TestCreateUser:
    """Тестирует метод _create_user."""

    @pytest.mark.parametrize(
        'user, expected', (
            pytest.param(
                user_list[0], user_list[0], id='user 1',
            ),
            pytest.param(
                user_list[1], user_list[1], id='user 2',
            ),
        ),
    )
    def test_create_user(
        self, user: User, expected: User, service: AuthService,
    ):
        """Тестирует позитивные сценарии."""
        service.repository.create_user.return_value = expected

        response = service._create_user(user)  # noqa

        assert response.username == expected.username
        assert response.user_id == expected.user_id
        assert response.password_hash == expected.password_hash

    @pytest.mark.parametrize(
        'user, side_effect', (
            pytest.param(
                user_list[1],
                raise_repository_error,
                id='error in repository',
            ),
        ),
    )
    def test_create_user_raises(
        self, user: User, side_effect, service: AuthService,
    ):
        """Тестирует негативный сценарий."""
        service.repository.create_user.side_effect = side_effect

        with pytest.raises(RepositoryError):
            service._create_user(user)  # noqa


class TestCreateToken:
    """Тестирует метод _create_token."""

    @pytest.mark.parametrize(
        'user, expected_token', (
            pytest.param(
                user_list[0], token_list[0], id='user 1',
            ),
            pytest.param(
                user_list[1], token_list[1], id='user 2',
            ),
        ),
    )
    def test_create_token(
        self, user: User, expected_token: Token, service: AuthService,
    ):
        """Тестирует позитивные сценарии."""
        service.repository.create_token.return_value = expected_token

        response = service._create_token(user)  # noqa

        assert response.subject.username == expected_token.subject.username
        assert response.subject.user_id == expected_token.subject.user_id
        assert response.subject.password_hash == expected_token.subject.password_hash  # noqa
        assert response.issued_at == expected_token.issued_at
        assert response.encoded_token == expected_token.encoded_token

    @pytest.mark.parametrize(
        'user, side_effect', (
            pytest.param(
                user_list[1],
                raise_repository_error,
                id='error in repository',
            ),
        ),
    )
    def test_create_token_raises(
        self, user: User, side_effect, service: AuthService,
    ):
        """Тестирует негативный сценарий."""
        service.repository.create_token.side_effect = side_effect

        with pytest.raises(RepositoryError):
            service._create_token(user)  # noqa
