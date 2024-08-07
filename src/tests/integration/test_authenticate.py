from collections import namedtuple
from datetime import datetime

import pytest

from app.core.authentication import AuthService, Token, User
from app.core.errors import AuthorizationError, NotFoundError
from app.core.models import UserCredentials

TestUser = namedtuple('TestUser', 'username, password')

test_user1 = TestUser('george', 'password_1')
test_user2 = TestUser('peter', 'password_2')


class TestRegister:
    """Тестирует метод register."""

    register_fields = 'user_creds'

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        register_fields, (
            pytest.param(
                UserCredentials(
                    username=test_user1.username,
                    password=test_user1.password,
                ),
                id='valid user 1',
            ),
            pytest.param(
                UserCredentials(
                    username=test_user2.username,
                    password=test_user2.password,
                ),
                id='valid user 2',
            ),
        ),
    )
    async def test_register(
        self, user_creds, service: AuthService,
    ):
        """Тестирует метод register."""
        token = await service.register(user_creds)

        if token is not None:
            assert token.subject == user_creds.username
            assert token.encoded_token
            assert token.issued_at
        else:
            raise AssertionError()


class TestAuthenticate:
    """Тестирует метод authenticate."""

    is_not_none = False
    is_none = True

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'user_creds, service_state_factory', (
            pytest.param(
                UserCredentials(
                    username=test_user1.username,
                    password=test_user1.password,
                ),
                'service_db_user_yes_token_no',
                id='user in db without token',
            ),
            pytest.param(
                UserCredentials(
                    username=test_user1.username,
                    password=test_user1.password,
                ),
                'service_db_user_yes_token_yes',
                id='user in db with token',
            ),
        ),
    )
    async def test_authenticate(
        self,
        user_creds,
        service_state_factory,
        request,
    ):
        """Тестирует метод authenticate."""
        factory = request.getfixturevalue(service_state_factory)
        srv: AuthService = await factory(
            user_creds.username, user_creds.password,
        )
        token_value = srv.encoder.encode(
            User(
                username=test_user1.username,
                password_hash=srv.hash.get(user_creds.password),
                user_id=1,
            ),
        )
        auth_header = f'Bearer {token_value.encoded_token}'

        token: Token | None = await srv.authenticate(
            user_creds, auth_header,
        )

        assert token is not None
        assert token.subject == user_creds.username

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'user_creds, service_state_factory, expected_error', (
            pytest.param(
                UserCredentials(
                    username=test_user1.username,
                    password=test_user1.password,
                ),
                'service_db_user_not_in_db',
                NotFoundError,
                id='user not in db',
            ),
            pytest.param(
                UserCredentials(
                    username=test_user1.username,
                    password=test_user1.password,
                ),
                'service_db_user_with_invalid_pass',
                AuthorizationError,
                id='user has invalid password',
            ),
        ),
    )
    async def test_authenticate_raises(
        self,
        user_creds,
        service_state_factory,
        expected_error,
        request,
    ):
        """Тестирует метод authenticate."""
        factory = request.getfixturevalue(service_state_factory)
        srv: AuthService = await factory(
            user_creds.username, user_creds.password,
        )
        password_hash = srv.hash.get(user_creds.password)
        token_value = srv.encoder.encode(
            User(
                username=test_user1.username,
                password_hash=password_hash,
                user_id=1,
            ),
        )
        auth_header = f'Bearer {token_value.encoded_token}'

        with pytest.raises(expected_error):
            await srv.authenticate(user_creds, auth_header)


class TestCheckToken:
    """Тестирует метод check_token."""

    user_credentials = UserCredentials(
        username=test_user1.username,
        password=test_user1.password,
    )
    is_expired = True
    is_not_expired = False
    expired_date = datetime(year=2024, month=1, day=1)  # noqa: WPS432 not magic

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'user_creds, service_state_and_token_factory', (
            pytest.param(
                user_credentials,
                'service_db_token_found',
                id='token found in cache',
            ),
            pytest.param(
                user_credentials,
                'service_db_token_not_found',
                id='token not found in cache',
                marks=pytest.mark.xfail(raises=NotFoundError),
            ),
        ),
    )
    async def test_check_token(
        self,
        user_creds,
        service_state_and_token_factory,
        request,
    ):
        """Тестирует метод check_token."""
        factory = request.getfixturevalue(service_state_and_token_factory)
        srv, token = await factory(
            user_creds.username, user_creds.password,
        )
        auth_header = f'Bearer {token.encoded_token}'

        assert await srv.check_token(auth_header)

    @pytest.mark.parametrize(
        'token, is_expired', (
            pytest.param(
                Token(  # noqa: S106 test value
                    subject=test_user1.username,
                    issued_at=datetime.now(),
                    encoded_token='test_value',
                ),
                is_not_expired,
            ),
            pytest.param(
                Token(  # noqa: S106 test value
                    subject=test_user1.username,
                    issued_at=expired_date,
                    encoded_token='test_value',
                ),
                is_expired,
            ),
        ),
    )
    def test_token_is_expired(self, token: Token, is_expired):
        """Тестирует метод is_expired."""
        assert token.is_expired() == is_expired
