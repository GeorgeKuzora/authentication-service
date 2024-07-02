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

        Создает, сохраняет в базе данных
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
        self.users.append(indexed_user)
        self.users_count += 1
        logger.info(f'Добавил пользователя {indexed_user} в хранилище')
        return indexed_user

    def create_token(self, token: Token) -> Token:
        """
        Создает токен в базе данных.

        Создает, сохраняет в базе данных
        и возвращает индексированную запись о токене пользователя.

        Args:
            token: Token - неидексированная запись о токене пользователя.

        Returns:
            Token - индексированная запись о токене пользователя.
        """
        indexed_token = Token(
            subject=token.subject,
            issued_at=token.issued_at,
            encoded_token=token.encoded_token,
            token_id=self.tokens_count
        )
        self.tokens.append(indexed_token)
        self.tokens_count += 1
        logger.info(f'Добавил токен {indexed_token} в хранилище')
        return indexed_token

    def get_user(self, user: User) -> User | None:
        """
        Получает пользователя из базы данных.

        Получает и возвращает запись о пользователе из базы данных.

        Args:
            user: User - данные пользователя.

        Returns:
            User | None - запись о пользователе в базе данных.
        """
        try:
            in_db_user, *_ = [
                member for member in self.users if (
                    member.username == user.username
                )
            ]
        except ValueError:
            logger.info(f'Пользователь {user} не найден в хранилище')
            return None

        logger.info(f'Получил пользователя {in_db_user} из хранилища')
        return in_db_user

    def get_token(self, user: User) -> Token | None:
        """
        Получает токен пользователя из базы данных.

        Получает и возвращает запись о токене пользователя из базы данных.

        Args:
            user: User - данные пользователя.

        Returns:
            Token | None - запись о токене пользователя в базе данных.
        """
        try:
            token, *_ = [
                member for member in self.tokens if (
                    member.subject.user_id == user.user_id
                )
            ]
        except ValueError:
            logger.info(f'Токен для пользователя {user} не найден')
            return None

        logger.info(f'Получил токен {token} из хранилища')
        return token

    def update_token(self, token: Token) -> Token:
        """
        Обновляет токен пользователя из базы данных.

        Обновляет и возвращает запись о токене пользователя из базы данных.

        Args:
            token: Token - данные о токене.

        Returns:
            Token | None - запись о токене пользователя в базе данных.
        """
        try:
            in_db_token, *_ = [
                member for member in self.tokens if (
                    member.subject.user_id == token.subject.user_id
                )
            ]
        except ValueError:
            logger.info(f'Токен для пользователя {token.subject} не найден')
            return self.create_token(token)

        token_position = self.tokens.index(in_db_token)
        token.token_id = in_db_token.token_id
        self.tokens[token_position] = token
        logger.info(f'Обновил токен {token} в хранилище')
        return token
