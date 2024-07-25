from app.core.authentication import Hash
from app.core.models import Token


class TokenCache:
    """Имплементация кэша для хранения токена."""

    def __init__(self) -> None:
        """Метод инициализации."""
        self.hash = Hash()
        self.storage = {}

    async def get_cache(self, cached_value: Token) -> Token:
        """
        Получает значение из кэша.

        :param cached_value: Кэшированное значение
        :type cached_value: Token
        :return: Кэшированное значение
        :rtype: Token
        :raises KeyError: Значение не найдено в кэше
        """
        key = self.hash.get(str(cached_value))
        token = self.storage.get(key)
        if token:
            return token
        raise KeyError(f'{cached_value} not found')

    async def create_cache(self, cached_value: Token) -> None:
        """
        Записывает значение в кэш.

        :param cached_value: Кэшируемое значение
        :type cached_value: Token
        """
        key = self.hash.get(str(cached_value))
        self.storage[key] = cached_value
