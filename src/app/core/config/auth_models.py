import logging
import os
from pathlib import Path

import dotenv

from app.core.errors import ConfigError

logger = logging.getLogger(__name__)


class AuthConfigAccessData:
    """
    Данные для доступа к конфигурации сервиса аутентификации.

    Attributes:
        algorithm_key: str - название переменной алгоритма.
        secret_key_key : str - название переменной секретного ключа.
        jwt_secrets_path : str - путь к файлу секретов.
    """

    def __init__(self) -> None:
        """Метод инициализации."""
        self.algorithm_key: str = 'TOKEN_ALGORITHM'
        self.secret_key_key: str = 'SECRET_KEY'
        self.jwt_secrets_path: str | None = os.environ.get('SECRETS_PATH')
        self._validate_access_data()

    def _is_valid_path(self, path: str) -> bool:
        passlib_path = Path(path)
        return passlib_path.is_file()

    def _validate_access_data(self) -> None:
        if self.jwt_secrets_path is None:
            logger.critical(
                'config file path not found. Set SECRETS_PATH=',
            )
            raise ConfigError(detail='config file path not found')
        elif not self._is_valid_path(self.jwt_secrets_path):
            logger.critical(
                f'auth config file {self.jwt_secrets_path} not found',
            )
            raise ConfigError(
                detail=f'auth config file {self.jwt_secrets_path} not found',
            )


class AuthConfig:
    """Данные для доступа к конфигурации сервиса аутентификации."""

    def __init__(self, access_data: AuthConfigAccessData) -> None:
        """
        Метод инициализации.

        :param access_data: данные для доступа к значениям конфигурации
        :type access_data: AuthConfigAccessData
        """
        jwt_config: dict[str, str | None] = dotenv.dotenv_values(
            dotenv_path=access_data.jwt_secrets_path,
        )
        algorithm_value: str | None = jwt_config.get(
            access_data.algorithm_key,
        )
        secret_key_value: str | None = jwt_config.get(
            access_data.secret_key_key,
        )

        self._validate_config_values(algorithm_value, secret_key_value)

        # set after validation
        self.algorithm: str = algorithm_value  # type: ignore
        self.secret_key: str = secret_key_value  # type: ignore

    def _validate_config_values(
        self, algorithm_value, secret_key_value,
    ) -> None:
        if algorithm_value is None:
            logger.critical('token algorithm was not provided')
            raise ConfigError(detail='token algorithm was not provided')
        if secret_key_value is None:
            logger.critical('secret key was not provided')
            raise ConfigError(detail='secret key was not provided')
