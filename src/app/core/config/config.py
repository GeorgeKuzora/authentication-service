import logging
import os
from functools import lru_cache

from app.core.config.auth_models import AuthConfig, AuthConfigAccessData
from app.core.config.settings_models import Settings
from app.core.errors import ConfigError

logger = logging.getLogger(__name__)


def get_auth_config() -> AuthConfig:
    """
    Возвращает конфигурацию сервиса аутетнификации.

    Получает данные из файла конфигурации и возращает
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
    """Создает конфигурацию сервиса."""
    config_path_env_var = 'CONFIG_PATH'
    config_file = os.getenv(config_path_env_var)
    return Settings.from_yaml(config_file)
