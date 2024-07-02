import logging

from app.service import Token, User

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
        """Метод инициализации."""
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
        logger.info(f'Created user {indexed_user}')
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
            token_id=self.tokens_count,
        )
        self.tokens.append(indexed_token)
        self.tokens_count += 1
        logger.info(f'Created token {indexed_token}')
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
            logger.warning(f'{user} is not found')
            return None

        logger.info(f'got {in_db_user}')
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
            logger.warning(f'token for {user} is not found')
            return None

        logger.info(f'got {token}')
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
        token_in_db = self.get_token(token.subject)
        if token_in_db is None:
            token_in_db = self.create_token(token)

        token_position = self.tokens.index(token_in_db)
        token.token_id = token_in_db.token_id
        self.tokens[token_position] = token
        logger.info(f'Updated {token}')
        return token
