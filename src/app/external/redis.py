import logging
from typing import Any

import redis

from app.core.config.config import get_settings
from app.core.errors import ServerError
from app.core.models import Token

logger = logging.getLogger(__name__)


class TokenCache:
    """Имплементация кэша для хранения токена."""

    def __init__(self) -> None:
        """Метод инициализации."""
        settings = get_settings()
        self.storage = redis.Redis(
            host=settings.redis.host,
            port=settings.redis.port,
            decode_responses=settings.redis.decode_responses,
        )

    async def get_cache(self, cache_value: Token) -> Token:
        """
        Получает значение из кэша.

        :param cache_value: Кэшированное значение
        :type cache_value: Token
        :return: Кэшированное значение
        :rtype: Token
        :raises KeyError: Значение не найдено в кэше
        :raises ServerError: Ошибка доступа к кэшу
        """
        key = self._get_key(cache_value)
        try:
            value_from_cache: dict[str, Any] = self.storage.hgetall(key)  # type:ignore # noqa: E501
        except Exception as exc:
            logger.error('error during cache access', exc_info=exc)
            raise ServerError() from exc
        if value_from_cache:
            logger.debug(f'got value from cache {value_from_cache}')
            return self._get_token(value_from_cache)
        logger.debug(f'cached value not found: {cache_value}')
        raise KeyError(f'{cache_value} not found')

    async def create_cache(self, cache_value: Token) -> None:
        """
        Записывает значение в кэш.

        :param cache_value: Кэшируемое значение
        :type cache_value: Token
        """
        key = self._get_key(cache_value)
        mapping = self._get_mapping(cache_value)
        self.storage.hset(key, mapping=mapping)

    def _get_key(self, token: Token) -> str:
        return f'username:{token.subject}'

    def _get_mapping(self, token: Token) -> dict[str, Any]:
        return token.model_dump()  # type:ignore # return the same signature

    def _get_token(self, cache_value: dict[str, Any]) -> Token:
        return Token(**cache_value)
