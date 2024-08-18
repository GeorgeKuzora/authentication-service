import logging

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.models import User as SrvUser
from app.external.postgres.models import User as DBUser
from app.external.postgres.storage import DBStorage

logger = logging.getLogger(__name__)

test_user = SrvUser(  # noqa: S106 test password hash
    username='george',
    password_hash='password_hash',
)


@pytest.fixture
def storage() -> DBStorage:
    """Создает объект DBStorage."""
    return DBStorage()


@pytest.fixture
def storage_with_user(storage: DBStorage):
    """Создает объект DBStorage с добавленным пользователем."""
    with Session(storage.pool) as session:
        user = DBUser(
            username=test_user.username,
            hashed_password=test_user.password_hash,
        )
        session.add(user)
        session.commit()
        try:
            yield storage
        except Exception:
            logger.debug('exception in tests with storage_with_user')
        finally:
            session.delete(user)
            session.commit()


@pytest.fixture
def storage_without_user(storage: DBStorage):
    """Создает объект DBStorage без пользователей."""
    with Session(storage.pool) as session:
        try:
            yield storage
        except Exception:
            logger.debug('exception in tests with storage_with_user')
        finally:
            user = session.scalars(
                select(DBUser).where(DBUser.username == test_user.username),
            ).first()
            if user is not None:
                session.delete(user)
                session.commit()
