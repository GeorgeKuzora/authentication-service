import pytest
from fastapi import status
from httpx import AsyncClient

from app.service import app


@pytest.fixture(scope='session')
def client():
    """Создает тестовый клиент."""
    return AsyncClient(app=app, base_url='http://test')


class TestRegister:
    """Тестирует хэндлер register."""

    valid_request = {'username': 'george', 'password': 'password123'}
    invalid_request = {'user_id': 'peter', 'pass': 'passw'}
    url = '/register'

    @pytest.mark.asyncio
    @pytest.mark.anyio
    async def test_valid_request_status(self, client: AsyncClient):
        """Тестирует метод register успешный ответ."""
        response = await client.post(self.url, json=self.valid_request)
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    @pytest.mark.anyio
    async def test_valid_request_body(self, client: AsyncClient):
        """Тестирует метод register тело ответа."""
        response = await client.post(self.url, json=self.valid_request)
        assert response.json()['subject'] == self.valid_request['username']

    @pytest.mark.asyncio
    @pytest.mark.anyio
    async def test_invalid_request_status(self, client: AsyncClient):
        """Тестирует метод register 422 ошибка."""
        response = await client.post(self.url, json=self.invalid_request)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
