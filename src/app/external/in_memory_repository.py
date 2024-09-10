import logging

from app.core.authentication import Token, User

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

    async def create_user(self, user: User) -> User:
        """
        Создает пользователя в базе данных.

        Создает, сохраняет в базе данных
        и возвращает индексированную запись о пользователе.

        :param user: неиндексированная запись о пользователе.
        :type user: User
        :return: индексированная запись о пользователе.
        :rtype: User
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

    async def create_token(self, token: Token) -> Token:
        """
        Создает токен в базе данных.

        Создает, сохраняет в базе данных
        и возвращает индексированную запись о токене пользователя.

        :param token: неиндексированная запись о токене пользователя.
        :type token: Token
        :return: индексированная запись о токене пользователя.
        :rtype: Token
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

    async def get_user(self, user: User) -> User | None:
        """
        Получает пользователя из базы данных.

        Получает и возвращает запись о пользователе из базы данных.

        :param user: неиндексированная запись о пользователе.
        :type user: User
        :return: индексированная запись о пользователе.
        :rtype: User
        """
        try:
            in_db_user = [
                member for member in self.users if (
                    member.username == user.username
                )
            ][0]
        except IndexError:
            logger.warning(f'{user} is not found')
            return None

        logger.info(f'got {in_db_user}')
        return in_db_user

    async def get_token(self, user: User) -> Token | None:
        """
        Получает токен пользователя из базы данных.

        Получает и возвращает запись о токене пользователя из базы данных.

        :param user: неиндексированная запись о пользователе.
        :type user: User
        :return: индексированная запись о токене  пользователе.
        :rtype: Token
        """
        try:
            token = [
                member for member in self.tokens if (
                    member.subject == user.username
                )
            ][0]
        except IndexError:
            logger.warning(f'token for {user} is not found')
            return None

        logger.info(f'got {token}')
        return token

    async def update_token(self, token: Token) -> Token:
        """
        Обновляет токен пользователя из базы данных.

        Обновляет и возвращает запись о токене пользователя из базы данных.

        :param token: неиндексированная запись о токене пользователя.
        :type token: Token
        :return: индексированная запись о токене пользователя.
        :rtype: Token
        """
        token_in_db = await self._get_token(token.subject)
        if token_in_db is None:
            token_in_db = await self.create_token(token)

        token_position = self.tokens.index(token_in_db)
        token.token_id = token_in_db.token_id
        self.tokens[token_position] = token
        logger.info(f'Updated {token}')
        return token

    async def _get_token(self, username: str) -> Token | None:
        """
        Получает токен пользователя из базы данных.

        Получает и возвращает запись о токене пользователя из базы данных.

        :param username: Имя пользователя
        :type username: str
        :return: индексированная запись о токене  пользователе.
        :rtype: Token
        """
        try:
            token = [
                member for member in self.tokens if (
                    member.subject == username
                )
            ][0]
        except IndexError:
            logger.warning(f'token for {username} is not found')
            return None

        logger.info(f'got {token}')
        return token
