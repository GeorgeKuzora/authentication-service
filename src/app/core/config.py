import logging
import os
from dataclasses import dataclass
from pathlib import Path

import dotenv

from app.core.authentication import Config  # type: ignore

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """
    Исключение возникающее в ходе конфигурации.

    Импортировать в имплементации репозитория данных,
    для вызова исключения при ошибке доступа к данным.
    """


@dataclass
class AuthConfigAccessData:
    """
    Данные для доступа к конфигурации сервиса аутентификации.

    Attributes:
        algorithm_key: str - название переменной алгоритма.
        secret_key_key : str - назывние переменной секретного ключа.
        jwt_secrets_path : str - путь к файлу секретов.
    """

    algorithm_key: str = 'TOKEN_ALGORITHM'
    secret_key_key: str = 'SECRET_KEY'
    jwt_secrets_path: str | None = os.environ.get('SECRETS_PATH')


def _is_valid_path(path: str) -> bool:
    passlib_path = Path(path)
    return passlib_path.is_file()


def get_auth_config() -> Config:
    """
    Возвращает конфигурацию сервиса аутетнификации.

    Получает данные из файла конфигурации и возращает
    объект конфигурации сервиса.

    Returns:
        Config - данные конфигурации сервиса.

    Raises:
        ConfigError - в случае если конфигурация не найдена.
    """
    access_data = AuthConfigAccessData()

    if access_data.jwt_secrets_path is None:
        logger.critical(
            'config file path not found. Set SECRETS_PATH=',
        )
        raise ConfigError(
            'config file path not found',
        )

    if not _is_valid_path(access_data.jwt_secrets_path):
        logger.critical(
            f'config file {access_data.jwt_secrets_path} not found',
        )
        raise ConfigError(
            f'config file {access_data.jwt_secrets_path} not found',
        )

    jwt_config: dict[str, str | None] = dotenv.dotenv_values(
        dotenv_path=access_data.jwt_secrets_path,
    )

    algorithm_value: str | None = jwt_config.get(access_data.algorithm_key)
    if algorithm_value is None:
        logger.critical('token algorithm was not provided')
        raise ConfigError('token algorithm was not provided')

    secret_key_value: str | None = jwt_config.get(access_data.secret_key_key)
    if secret_key_value is None:
        logger.critical('secret key was not provided')
        raise ConfigError('secret key was not provided')

    return Config(
        token_algorithm=algorithm_value, secret_key=secret_key_value,
    )
