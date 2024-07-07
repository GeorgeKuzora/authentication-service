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
