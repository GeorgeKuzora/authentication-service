import logging

from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session

from app.core import models as srv
from app.core.config.config import get_settings
from app.core.errors import RepositoryError
from app.external.postgres import models as db

logger = logging.getLogger(__name__)


def create_pool() -> Engine:
    """
    Создает sqlalchemy engine с пулом соединений.

    :return: sqlalchemy engine
    :rtype: Engine
    """
    settings = get_settings()
    return create_engine(
        str(settings.postgres.pg_dns),
        pool_size=settings.postgres.pool_size,
        max_overflow=settings.postgres.max_overflow,
    )


def create_all_tables() -> None:
    """Создает таблицы в базе данных."""
    pool = create_pool()
    db.Base.metadata.create_all(pool)


class DBStorage:
    """База данных."""

    def __init__(self) -> None:
        """Метод инициализации."""
        self.pool = create_pool()

    async def create_user(self, user: srv.User) -> srv.User:
        """
        Абстрактный метод создания пользователя.

        :param user: объект пользователя
        :type user: User
        :return: Пользователь созданный в базе данных.
        :rtype: srv.User
        :raises RepositoryError: При ошибке в базе данных
        """
        with Session(self.pool) as session:
            db_user = self._get_db_user(user, session)
            if db_user:
                return self._get_srv_user(db_user)
            db_user = db.User(
                username=user.username,
                hashed_password=user.password_hash,
            )
            try:
                session.add(db_user)
            except Exception as err:
                logger.error(f"repository error can't create {user.username}")
                raise RepositoryError(
                    detail=f"can't create {user.username}",
                ) from err
            try:
                session.commit()
            except Exception as com_err:
                logger.error(f"can't commit create user: {user.username}")
                raise RepositoryError(
                    detail=f"can't commit create user {user.username}",
                ) from com_err
            srv_user = self._get_srv_user(db_user)
        return srv_user

    async def get_user(self, user: srv.User) -> srv.User | None:
        """
        Абстрактный метод получения токена.

        :param user: объект пользователя
        :type user: User
        :return: Пользователь в базе данных
        :rtype: srv.User | None
        """
        with Session(self.pool) as session:
            db_user = self._get_db_user(user, session)
            if db_user is not None:
                return self._get_srv_user(db_user)
            return None

    def _get_db_user(self, user: srv.User, session: Session) -> db.User | None:
        try:
            return session.scalars(
                select(db.User).where(db.User.username == user.username),
            ).first()
        except Exception as err:
            logger.error(f"repository error can't get {user.username}")
            raise RepositoryError(
                detail=f"can't get {user.username}",
            ) from err

    def _get_srv_user(self, db_user: db.User) -> srv.User:
        return srv.User(
            username=db_user.username,
            password_hash=db_user.hashed_password,
            user_id=db_user.id,
        )
