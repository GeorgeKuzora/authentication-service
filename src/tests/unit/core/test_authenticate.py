import pytest

from app.core.authentication import AuthService
from app.core.errors import AuthorizationError, NotFoundError, RepositoryError
from app.core.models import User, UserCredentials
from tests.unit.conftest import token_list, user_list

param_fields = 'user_creds, expected_token'
param_fields_with_side_effect = 'user_creds, side_effect'

test_encoded_token_value = 'Bearer sfasdf343ad343'  # noqa: S105 test value


def raise_repository_error(*args, **kwargs):
    """Функция для вызова RepositoryError."""
    raise RepositoryError


class TestRegister:
    """Тестирует метод register."""

    passwords = ['plain_password1', 'plain_password2']

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        param_fields, (
            pytest.param(
                UserCredentials(
                    username=user_list[0].username,
                    password=passwords[0],
                ),
                token_list[0],
                id='valid user 1',
            ),
            pytest.param(
                UserCredentials(
                    username=user_list[1].username,
                    password=passwords[1],
                ),
                token_list[1],
                id='valid user 2',
            ),
        ),
    )
    async def test_register(
        self, user_creds: UserCredentials, expected_token, service: AuthService,
    ):
        """Тестирует позитивные сценарии."""
        service.repository.create_user.return_value = User(
            username=user_creds.username, password_hash=user_creds.password,
        )

        recieved_token = await service.register(user_creds=user_creds)

        assert isinstance(recieved_token, type(expected_token))
        if recieved_token is not None:
            assert recieved_token.subject == expected_token.subject

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        param_fields_with_side_effect, (
            pytest.param(
                UserCredentials(
                    username=user_list[0].username,
                    password=passwords[0],
                ),
                raise_repository_error,
                id='error in repository',
            ),
            pytest.param(
                UserCredentials(
                    username=user_list[0].username,
                    password=passwords[0],
                ),
                raise_repository_error,
                id='error in repository',
            ),
        ),
    )
    async def test_register_raises(
        self, user_creds: UserCredentials, side_effect, service: AuthService,
    ):
        """Тестирует негативные сценарии."""
        service.repository.create_user.side_effect = side_effect

        with pytest.raises(RepositoryError):
            await service.register(user_creds)


class TestAuthenticate:
    """Тестирует метод authenticate."""

    passwords = ['plain_password1', 'plain_password2']

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        param_fields, (
            pytest.param(
                UserCredentials(
                    username=user_list[0].username,
                    password=passwords[0],
                ),
                token_list[0],
                id='update token',
            ),
        ),
    )
    async def test_authenticate_token_update(
        self,
        user_creds: UserCredentials,
        expected_token,
        srv_encoder_mock: AuthService,
    ):
        """Тестирует сценарий пользователь и токен пользователя найдены."""
        encoded_token_value = test_encoded_token_value
        password_hash = srv_encoder_mock.hash.get(user_creds.password)
        user = User(
            username=user_creds.username,
            password_hash=password_hash,
            user_id=1,
        )
        srv_encoder_mock.repository.get_user.return_value = user
        srv_encoder_mock.cache.get_cache.return_value = expected_token
        srv_encoder_mock.repository.update_token.return_value = expected_token

        recieved_token = await srv_encoder_mock.authenticate(
            user_creds, encoded_token_value,
        )

        assert isinstance(recieved_token, type(expected_token))
        if recieved_token is not None:
            assert recieved_token == expected_token
        else:
            raise AssertionError()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        param_fields, (
            pytest.param(
                UserCredentials(
                    username=user_list[0].username,
                    password=passwords[0],
                ),
                token_list[0],
                id='create token',
            ),
        ),
    )
    async def test_authenticate_token_create(
        self,
        user_creds: UserCredentials,
        expected_token,
        srv_encoder_mock: AuthService,
    ):
        """Тестирует сценарий токен пользователя не найден."""
        encoded_token_value = test_encoded_token_value
        password_hash = srv_encoder_mock.hash.get(user_creds.password)
        user = User(
            username=user_creds.username,
            password_hash=password_hash,
            user_id=1,
        )
        srv_encoder_mock.repository.get_user.return_value = user
        srv_encoder_mock.cache.get_cache.return_value = None
        srv_encoder_mock.encoder.encode.return_value = expected_token

        recieved_token = await srv_encoder_mock.authenticate(
            user_creds, encoded_token_value,
        )

        assert isinstance(recieved_token, type(expected_token))
        if recieved_token is not None:
            assert recieved_token == expected_token
        else:
            raise AssertionError()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        param_fields, (
            pytest.param(
                UserCredentials(
                    username=user_list[0].username,
                    password=passwords[0],
                ),
                token_list[0],
                id='user not found token is None',
            ),
        ),
    )
    async def test_authenticate_user_not_found(
        self,
        user_creds: UserCredentials,
        expected_token,
        srv_encoder_mock: AuthService,
    ):
        """Тестирует сценарий пользователь не найден."""
        encoded_token_value = test_encoded_token_value
        srv_encoder_mock.repository.get_user.return_value = None

        with pytest.raises(NotFoundError):
            await srv_encoder_mock.authenticate(
                user_creds, encoded_token_value,
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        param_fields, (
            pytest.param(
                UserCredentials(
                    username=user_list[0].username,
                    password=passwords[0],
                ),
                token_list[0],
                id='not veirfied token is None',
            ),
        ),
    )
    async def test_authenticate_user_not_verified(
        self,
        user_creds: UserCredentials,
        expected_token,
        srv_encoder_mock: AuthService,
    ):
        """Тестирует сценарий пользователь верифицирован."""
        encoded_token_value = test_encoded_token_value
        password_hash = srv_encoder_mock.hash.get('invalid_pass')
        user = User(
            username=user_creds.username,
            password_hash=password_hash,
            user_id=1,
        )
        srv_encoder_mock.repository.get_user.return_value = user

        with pytest.raises(AuthorizationError):
            await srv_encoder_mock.authenticate(
                user_creds, encoded_token_value,
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        param_fields, (
            pytest.param(
                UserCredentials(
                    username=user_list[0].username,
                    password=passwords[0],
                ),
                token_list[0],
                id='raises RepositoryError',
            ),
        ),
    )
    async def test_authenticate_raises(
        self,
        user_creds: UserCredentials,
        expected_token,
        srv_encoder_mock: AuthService,
    ):
        """Тестирует возврат ошибки при ошибке в репозитории."""
        encoded_token_value = test_encoded_token_value
        srv_encoder_mock.repository.get_user.side_effect = raise_repository_error  # noqa: E501 can't make shorter
        srv_encoder_mock.repository.get_token.side_effect = raise_repository_error  # noqa: E501 can't make shorter
        srv_encoder_mock.repository.create_token.side_effect = raise_repository_error  # noqa: E501 can't make shorter

        with pytest.raises(RepositoryError):
            await srv_encoder_mock.authenticate(
                user_creds, encoded_token_value,
            )
