import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.core.config.config import get_auth_config
from app.core.config.models import AuthConfig, AuthConfigAccessData
from app.core.errors import ConfigError


class TestAuthConfigAccessData:
    """Тестирует методы класса AuthConfigAccessData."""

    file_name = 'secrets'

    @pytest.fixture
    def valid_file_path(self, tmp_path):
        """
        Фикстура для создания тестового файла.

        :param tmp_path: фикстура pytest для работы во временной директории.
        :yield: путь к созданному файлу
        :ytype: Path
        """
        file_path = tmp_path / self.file_name
        with open(file_path, 'w') as tmp_file:
            tmp_file.write('\n')
        yield file_path
        os.remove(file_path)

    @pytest.fixture
    def invalid_file_path(self):
        """Фикстура для получения неверного пути к файлу."""
        return Path('/invalid_tmp_file_path')

    @pytest.fixture
    def path_is_none(self):
        """Фикстура для получения значения None."""
        pass  # noqa: WPS420 need for parametrization

    @pytest.mark.parametrize(
        'file_path_fixture', (
            pytest.param(
                'valid_file_path',
                id='valid file path',
            ),
            pytest.param(
                'invalid_file_path',
                id='file not found on path',
                marks=pytest.mark.xfail(raises=ConfigError),
            ),
            pytest.param(
                'path_is_none',
                id='path is none',
                marks=pytest.mark.xfail(raises=ConfigError),
            ),
        ),
    )
    def test_init(self, file_path_fixture, monkeypatch, request):
        """Тестирует метод инициализации объекта."""
        file_path = request.getfixturevalue(file_path_fixture)
        monkeypatch.setattr(
            'app.core.config.models.os.environ.get',
            lambda _: file_path,
        )
        access_data = AuthConfigAccessData()

        assert access_data.jwt_secrets_path == file_path


class TestAuthConfig:
    """Тестирует методы класса TestAuthConfig."""

    test_secret_key_key = 'SECRET_KEY'  # noqa: S105 test value
    test_algorithm_key = 'TOKEN_ALGORITHM'
    test_secret_key_value = '09d25e094faa6ca2556c818166b7a9563b93f7099f'  # noqa: S105, E501 test value
    test_algorithm_value = 'HS256'

    valid_config_values = {
        test_secret_key_key: test_secret_key_value,
        test_algorithm_key: test_algorithm_value,
    }

    config_values_no_secret_key = {
        test_secret_key_key: None,
        test_algorithm_key: test_algorithm_value,
    }
    config_values_no_algorithm = {
        test_secret_key_key: test_secret_key_value,
        test_algorithm_key: None,
    }

    @pytest.fixture
    def auth_access_data(self):
        """
        Фикстура для получения мок объекта AuthConfigAccessData.

        :return: мок объект AuthConfigAccessData
        :rtype: MagicMock
        """
        access_data = MagicMock()
        access_data.algorithm_key = self.test_algorithm_key
        access_data.secret_key_key = self.test_secret_key_key
        access_data.jwt_secrets_path = '/valid_path'
        return access_data

    @pytest.mark.parametrize(
        'config_values', (
            pytest.param(valid_config_values, id='valid values'),
        ),
    )
    def test_init(self, config_values, auth_access_data, monkeypatch):
        """Тестирует метод инициализации объекта."""
        monkeypatch.setattr(
            'app.core.config.models.dotenv.dotenv_values',
            lambda *args, **kwargs: config_values,
        )

        config = AuthConfig(auth_access_data)

        assert config.secret_key == self.test_secret_key_value
        assert config.algorithm == self.test_algorithm_value

    def test_init_raises_on_secret_key_is_none(
        self, auth_access_data, monkeypatch,
    ):
        """Тестирует возникновение ошибки если ключ не предоставлен."""
        monkeypatch.setattr(
            'app.core.config.models.dotenv.dotenv_values',
            lambda *args, **kwargs: self.config_values_no_secret_key,
        )

        with pytest.raises(ConfigError):
            AuthConfig(auth_access_data)

    def test_init_raises_on_algorithm_is_none(
        self, auth_access_data, monkeypatch,
    ):
        """Тестирует возникновение ошибки если алгоритм не предоставлен."""
        monkeypatch.setattr(
            'app.core.config.models.dotenv.dotenv_values',
            lambda *args, **kwargs: self.config_values_no_algorithm,
        )

        with pytest.raises(ConfigError):
            AuthConfig(auth_access_data)


class TestGetAuthConfig:
    """Тестирует функцию get_auth_config."""

    return_ok = True

    def raise_config_error(self):
        """Метод для вызова исключения ConfigError."""
        raise ConfigError

    def test_is_returns(self, monkeypatch):
        """Тестирует что возвращается значение конфигурации."""
        monkeypatch.setattr(
            'app.core.config.config.AuthConfigAccessData.__init__',
            lambda *args, **kwargs: None,
        )
        monkeypatch.setattr(
            'app.core.config.config.AuthConfig',
            lambda *args, **kwargs: self.return_ok,
        )

        function_return = get_auth_config()

        assert function_return == self.return_ok

    def test_data_access_error(self, monkeypatch):
        """Тестирует ошибку доступа к данным конфигурации."""
        monkeypatch.setattr(
            'app.core.config.models.AuthConfigAccessData.__init__',
            lambda *args, **kwargs: self.raise_config_error(),
        )

        with pytest.raises(ConfigError):
            get_auth_config()

    def test_config_values_error(self, monkeypatch):
        """Тестирует ошибку конфигурации."""
        monkeypatch.setattr(
            'app.core.config.models.AuthConfigAccessData.__init__',
            lambda *args, **kwargs: None,
        )
        monkeypatch.setattr(
            'app.core.config.models.AuthConfig.__init__',
            lambda *args, **kwargs: self.raise_config_error(),
        )

        with pytest.raises(ConfigError):
            get_auth_config()
