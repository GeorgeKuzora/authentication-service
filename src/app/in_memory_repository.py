import logging
from app.service import User, Token


logger = logging.getLogger(__name__)


class InMemoryRepository:
    """
    Имплементация хранилища данных в оперативной памяти.

    Сохраняет данные только на время работы программы.
    Для хранения данных использует списки python.

    Attributes:
        users: list[User] - созданные пользователи.
        users_count: int - счетчик созданных пользователей.
        tokens: list[Token] - созданные токены.
        tokens_count: int - счетчик созданных токенов.
    """

    def __init__(self) -> None:
        self.users: list[User] = []
        self.users_count: int = 0
        self.tokens: list[Token] = []
        self.tokens_count: int = 0

    def create_user(self, user: User) -> User:
        """
        Создает пользователя в базе данных.

        Создает, созраняет в базе данных
        и возвращает индексированную запись о пользователе.

        Args:
            user: User - неидексированная запись о пользователе.

        Returns:
            User - индексированная запись о пользователе.
        """
        indexed_user = User(
            username=user.username,
            password_hash=user.password_hash,
            user_id=self.users_count,
        )
        self.users_count += 1
        logger.info(f'Добавил пользователя {indexed_user} в хранилище')
        return indexed_user
