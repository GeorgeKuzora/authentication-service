import logging
import os
from functools import lru_cache

from app.core.config.auth_models import AuthConfig, AuthConfigAccessData
from app.core.config.settings_models import Settings
from app.core.errors import ConfigError

logger = logging.getLogger(__name__)


def get_auth_config() -> AuthConfig:
    """
    Возвращает конфигурацию сервиса аутентификации.

    Получает данные из файла конфигурации и возвращает
    объект конфигурации сервиса.

    :return: данные конфигурации сервиса.
    :rtype: Config
    :raises ConfigError: в случае если конфигурация не найдена.
    """
    try:
        access_data = AuthConfigAccessData()
    except ConfigError as access_error:
        logger.critical('auth config data access failed')
        raise ConfigError(
            detail='auth config data access failed',
        ) from access_error
    try:
        return AuthConfig(access_data)
    except ConfigError as config_error:
        logger.critical('auth config setting failed')
        raise ConfigError(detail='auth config setting failed') from config_error


@lru_cache
def get_settings() -> Settings:
    """
    Создает конфигурацию сервиса.

    :return: Объект с конфигурацией сервиса.
    :rtype: Settings
    :raises ConfigError: При ошибке в ходе конфигурации.
    """
    config_path_env_var = 'CONFIG_PATH'
    config_file = os.getenv(config_path_env_var)
    if config_file is None:
        logger.critical(f'env variable {config_path_env_var} not found')
        raise ConfigError(
            detail=f'env variable {config_path_env_var} not found',
        )
    return Settings.from_yaml(config_file)
