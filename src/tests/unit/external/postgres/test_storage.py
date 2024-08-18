import logging

import pytest

from app.core.models import User
from app.external.postgres.storage import DBStorage
from tests.unit.external.postgres.conftest import test_user

logger = logging.getLogger(__name__)


class TestCreateUser:
    """Тестирует метод create_user."""

    @pytest.mark.asyncio
    @pytest.mark.database
    @pytest.mark.parametrize(
        'storage_fixture, user', (
            pytest.param(
                'storage_with_user',
                test_user,
                id='storage with user',
            ),
            pytest.param(
                'storage_without_user',
                test_user,
                id='storage without user',
            ),
        ),
    )
    async def test_create_user(
        self, storage_fixture, user: User, request,
    ):
        """Тестирует что метод возвращает правильный объект."""
        storage: DBStorage = request.getfixturevalue(storage_fixture)

        db_user: User | None = await storage.create_user(user=user)

        assert db_user.username == user.username
        assert db_user.password_hash == user.password_hash


class TestGetUser:
    """Тестирует метод update_user."""

    @pytest.mark.asyncio
    @pytest.mark.database
    @pytest.mark.parametrize(
        'storage_fixture, user, expected', (
            pytest.param(
                'storage_with_user',
                test_user,
                test_user,
                id='storage with user',
            ),
            pytest.param(
                'storage_without_user',
                test_user,
                None,
                id='storage without user',
            ),
        ),
    )
    async def test_update_user(
        self, storage_fixture, user: User, expected: User, request,
    ):
        """Тестирует что метод возвращает правильный объект."""
        storage: DBStorage = request.getfixturevalue(storage_fixture)

        db_user: User | None = await storage.get_user(user=user)

        if db_user is None:
            assert db_user is expected
        else:
            assert db_user.username == expected.username
            assert db_user.password_hash == expected.password_hash
