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


class TestHashVerifyPassword:
    """Тестирует хэширование и верификацию пароля."""

    def test_hash_verify_password(self, service: AuthService):
        """Тестирует хэширование и верификацию пароля."""
        plain_password = 'plain-password'
        password_hash = service._get_password_hash(plain_password)  # noqa

        verified = service._verify_password(plain_password, password_hash)  # noqa

        assert verified


class TestGetUser:
    """Тестирует метод _get_user."""

    @pytest.mark.parametrize(
        'user, expected', (
            pytest.param(
                user_list[0], user_list[0], id='user 1',
            ),
            pytest.param(
                user_list[1], user_list[1], id='user 2',
            ),
            pytest.param(
                user_list[1], None, id='user not found',
            ),
        ),
    )
    def test_get_user(self, user: User, expected: User, service: AuthService):
        """Тестирует позитивные сценарии."""
        service.repository.get_user.return_value = expected

        response = service._get_user(user)  # noqa

        assert isinstance(response, type(expected))
        if response is not None:
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
    def test_get_user_raises(
        self, user: User, side_effect, service: AuthService,
    ):
        """Тестирует негативный сценарий."""
        service.repository.get_user.side_effect = side_effect

        with pytest.raises(RepositoryError):
            service._get_user(user)  # noqa


class TestGetToken:
    """Тестирует метод _get_token."""

    @pytest.mark.parametrize(
        'user, expected_token', (
            pytest.param(
                user_list[0], token_list[0], id='user 1',
            ),
            pytest.param(
                user_list[1], token_list[1], id='user 2',
            ),
            pytest.param(
                user_list[1], None, id='token not found',
            ),
        ),
    )
    def test_get_token(
        self, user: User, expected_token: Token, service: AuthService,
    ):
        """Тестирует позитивные сценарии."""
        service.repository.get_token.return_value = expected_token

        response = service._get_token(user)  # noqa

        assert isinstance(response, type(expected_token))
        if response is not None:
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
    def test_get_token_raises(
        self, user: User, side_effect, service: AuthService,
    ):
        """Тестирует негативный сценарий."""
        service.repository.get_token.side_effect = side_effect

        with pytest.raises(RepositoryError):
            service._get_token(user)  # noqa


class TestupdateToken:
    """Тестирует метод _update_token."""

    @pytest.mark.parametrize(
        'user, expected_token', (
            pytest.param(
                user_list[0], token_list[0], id='user 1',
            ),
            pytest.param(
                user_list[1], token_list[1], id='user 2',
            ),
            pytest.param(
                user_list[1], None, id='repository returned None',
            ),
        ),
    )
    def test_update_token(
        self, user: User, expected_token: Token, service: AuthService,
    ):
        """Тестирует позитивные сценарии."""
        service.repository.update_token.return_value = expected_token

        response = service._update_token(user)  # noqa

        assert isinstance(response, type(expected_token))
        if response is not None:
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
    def test_update_token_raises(
        self, user: User, side_effect, service: AuthService,
    ):
        """Тестирует негативный сценарий."""
        service.repository.update_token.side_effect = side_effect

        with pytest.raises(RepositoryError):
            service._update_token(user)  # noqa
