from enum import StrEnum

import pytest
import pytest_asyncio
from fastapi import status
from httpx import AsyncClient

from app.service import app
from tests.integration.conftest import get_service


class Fixtures(StrEnum):
    """Названия часто используетмых фикстур."""

    service_db_user_yes_token_no = 'service_db_user_yes_token_no'
    service_db_user_yes_token_yes = 'service_db_user_yes_token_yes'
    service_db_user_not_in_db = 'service_db_user_not_in_db'
    service_db_user_with_invalid_pass = 'service_db_user_with_invalid_pass'
    service_db_token_found = 'service_db_token_found'
    service_db_token_not_found = 'service_db_token_not_found'


class Key(StrEnum):
    """Часто встречающиеся в коде литералы."""

    username = 'username'
    credentials = 'credentials'
    headers = 'headers'
    password = 'password'  # noqa: S105 not a password
    authorization = 'Authorization'


bearer = 'Bearer'
encoded_token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnZW9yZ2UiLCJpYXQiOjE3MjI4NDgxODh9.A9xdaYu9KEpncR0tP_rcRZG_nkEBFddvmutKLnnKErQ'  # noqa: S105, E501 long token
valid_credentials = {Key.username: 'george', Key.password: 'password123'}
invalid_credentials = {'user_id': 'peter', 'pass': 'passw'}
valid_header = {Key.authorization: f'{bearer} {encoded_token}'}  # noqa: E501 cant make shorter
invalid_header_no_bearer = {Key.authorization: f'{encoded_token}'}  # noqa: E501 cant make shorter
invalid_header_invalid_value = {Key.authorization: f'{bearer} invalid_value'}
invalid_header_invalid_key = {'invalid-key': f'{bearer} {encoded_token}'}


@pytest_asyncio.fixture(scope='session')
async def client() -> AsyncClient:
    """Создает тестовый клиент."""
    service = get_service()
    app.service = service  # type: ignore # app has **extras specially for it
    return AsyncClient(app=app, base_url='http://test')


class TestRegister:
    """Тестирует хэндлер register."""

    url = '/register'

    @pytest.mark.asyncio
    @pytest.mark.anyio
    async def test_valid_request_status(self, client: AsyncClient):
        """Тестирует метод register успешный ответ."""
        response = await client.post(self.url, json=valid_credentials)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    @pytest.mark.anyio
    async def test_valid_request_body(self, client: AsyncClient):
        """Тестирует метод register тело ответа."""
        response = await client.post(self.url, json=valid_credentials)
        assert response.json()['subject'] == valid_credentials[Key.username]

    @pytest.mark.asyncio
    @pytest.mark.anyio
    async def test_invalid_request_status(self, client: AsyncClient):
        """Тестирует метод register 422 ошибка."""
        response = await client.post(self.url, json=invalid_credentials)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestAuthenticate:
    """Тестирует хэндлер authenticate."""

    url = '/login'

    @pytest.mark.asyncio
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        'request_data, builder_fixture, expected_status_code', (
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: valid_header,
                },
                Fixtures.service_db_user_yes_token_no,
                status.HTTP_200_OK,
                id='user in db, token not in db',
            ),
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: valid_header,
                },
                Fixtures.service_db_user_yes_token_yes,
                status.HTTP_200_OK,
                id='user in db, token in db',
            ),
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: valid_header,
                },
                Fixtures.service_db_user_not_in_db,
                status.HTTP_404_NOT_FOUND,
                id='user not in db',
            ),
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: valid_header,
                },
                Fixtures.service_db_user_with_invalid_pass,
                status.HTTP_401_UNAUTHORIZED,
                id='user has invalid password',
            ),
            pytest.param(
                {
                    Key.credentials: invalid_credentials,
                    Key.headers: valid_header,
                },
                Fixtures.service_db_user_yes_token_no,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                id='invalid credentials',
            ),
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: invalid_header_invalid_key,
                },
                Fixtures.service_db_user_yes_token_no,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                id='invalid header invalid key',
            ),
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: invalid_header_invalid_value,
                },
                Fixtures.service_db_user_yes_token_no,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                id='invalid header invalid value',
            ),
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: invalid_header_no_bearer,
                },
                Fixtures.service_db_user_yes_token_no,
                status.HTTP_401_UNAUTHORIZED,
                id='invalid header no bearer',
            ),
        ),
    )
    async def test_login(
        self,
        request_data,
        builder_fixture,
        expected_status_code,
        service_mocker,
        client: AsyncClient,
        request,
    ):
        """Тестирует login."""
        builder = request.getfixturevalue(builder_fixture)
        auth_service = await builder(
            request_data.get(Key.credentials).get(
                Key.username, invalid_credentials['user_id'],
            ),
            request_data.get(Key.credentials).get(
                Key.password, invalid_credentials['pass'],
            ),
        )
        service_mocker(auth_service)

        response = await client.post(
            self.url,
            json=request_data.get(Key.credentials),
            headers=request_data.get(Key.headers),
        )

        assert response.status_code == expected_status_code
        if expected_status_code == status.HTTP_200_OK:
            assert (
                response.json()['subject'] ==
                request_data.get(Key.credentials).get(Key.username)
            )


class TestCheckToken:
    """Тестирует хэндлер /check_token."""

    url = '/check_token'

    @pytest.mark.asyncio
    @pytest.mark.anyio
    @pytest.mark.parametrize(
        'request_data, builder_fixture, expected_status_code', (
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: valid_header,
                },
                Fixtures.service_db_token_found,
                status.HTTP_200_OK,
                id='token in db',
            ),
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: valid_header,
                },
                Fixtures.service_db_token_not_found,
                status.HTTP_404_NOT_FOUND,
                id='token not in db',
            ),
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: invalid_header_invalid_key,
                },
                Fixtures.service_db_token_found,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                id='invalid header invalid key',
            ),
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: invalid_header_invalid_value,
                },
                Fixtures.service_db_token_found,
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                id='invalid header invalid value',
            ),
            pytest.param(
                {
                    Key.credentials: valid_credentials,
                    Key.headers: invalid_header_no_bearer,
                },
                Fixtures.service_db_token_found,
                status.HTTP_401_UNAUTHORIZED,
                id='invalid header no bearer',
            ),
        ),
    )
    async def test_check_token(
        self,
        request_data,
        builder_fixture,
        expected_status_code,
        service_mocker,
        client: AsyncClient,
        request,
    ):
        """Тестирует check_token."""
        builder = request.getfixturevalue(builder_fixture)
        auth_service, token = await builder(
            request_data.get(Key.credentials).get(
                Key.username, invalid_credentials['user_id'],
            ),
            request_data.get(Key.credentials).get(
                Key.password, invalid_credentials['pass'],
            ),
        )
        service_mocker(auth_service)
        # Должен использовать токен созданный в базе данных
        if expected_status_code == status.HTTP_200_OK:
            headers = request_data.get(Key.headers)
            headers[Key.authorization] = f'Bearer {token.encoded_token}'  # type: ignore  # noqa: E501

        response = await client.post(
            self.url,
            headers=request_data[Key.headers],  # type: ignore  # noqa: E501
        )

        assert response.status_code == expected_status_code
