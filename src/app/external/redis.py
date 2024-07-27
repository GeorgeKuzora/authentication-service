from app.core.models import Token


class TokenCache:
    """Имплементация кэша для хранения токена."""

    def __init__(self) -> None:
        """Метод инициализации."""
        self.storage: dict[str, Token] = {}

    async def get_cache(self, cache_value: Token) -> Token:
        """
        Получает значение из кэша.

        :param cache_value: Кэшированное значение
        :type cache_value: Token
        :return: Кэшированное значение
        :rtype: Token
        :raises KeyError: Значение не найдено в кэше
        """
        key = cache_value.encoded_token
        token_value = self.storage.get(key)
        if token_value:
            return token_value
        raise KeyError(f'{cache_value} not found')

    async def create_cache(self, cache_value: Token) -> None:
        """
        Записывает значение в кэш.

        :param cache_value: Кэшируемое значение
        :type cache_value: Token
        """
        key = cache_value.encoded_token
        self.storage[key] = cache_value
