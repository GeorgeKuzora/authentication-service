import nest_asyncio
import pytest
import pytest_asyncio

from app.core.authentication import AuthService, User
from app.core.config.config import get_auth_config
from app.external.in_memory_repository import InMemoryRepository
from app.external.kafka import KafkaProducer
from app.external.redis import TokenCache

nest_asyncio.apply()


def get_service():
    """Создает экземпляр сервиса."""
    config = get_auth_config()
    repository = InMemoryRepository()
    cache = TokenCache()
    queue = KafkaProducer()
    return AuthService(
        repository=repository,
        config=config,
        cache=cache,
        producer=queue,
    )


@pytest_asyncio.fixture
async def service():
    """
    Фикстура создает экземпляр сервиса.

    Атрибуты сервиса repository, config являются реальными объектами.

    :return: экземпляр сервиса
    :rtype: AuthService
    """
    return get_service()


@pytest.fixture
def service_db_user_yes_token_no(service: AuthService):
    """
    Возвращает функцию для создания сервиса.

    Возвращаемая функция примает username и password
    и создает запись о пользователе в базе данных.

    :param service: экземпляр сервиса
    :type service: AuthService
    :return: функция создания сервиса
    :rtype: callable
    """
    async def _service_db_user_yes_token_no(username, password):  # noqa: WPS430, E501 need for service state parametrization
        user_id = 1
        user = User(
            username=username,
            password_hash=service.hash.get(password),
            user_id=user_id,
        )
        await service.repository.create_user(user)
        return service
    return _service_db_user_yes_token_no


@pytest.fixture
def service_db_user_yes_token_yes(service: AuthService):
    """
    Возвращает функцию для создания сервиса.

    Возвращаемая функция примает username и password,
    создает запись о пользователе в базе данных
    и добавляет токен для пользователя в базу данных.

    :param service: экземпляр сервиса
    :type service: AuthService
    :return: функция создания сервиса
    :rtype: callable
    """
    async def _service_db_user_yes_token_yes(username, password):  # noqa: WPS430, E501 need for service state parametrization
        user_id = 1
        user = User(
            username=username,
            password_hash=service.hash.get(password),
            user_id=user_id,
        )
        user = await service.repository.create_user(user)
        token = service.encoder.encode(user)
        await service.cache.create_cache(token)
        return service
    return _service_db_user_yes_token_yes


@pytest.fixture
def service_db_user_not_in_db(service: AuthService):
    """
    Возвращает функцию для создания сервиса.

    Возвращаемая функция примает username и password.
    Возвращаемая функция создвет сервис без записей в базе данных.

    :param service: экземпляр сервиса
    :type service: AuthService
    :return: функция создания сервиса
    :rtype: callable
    """
    async def _service_db_user_not_id_db(username, password):  # noqa: WPS430, E501 need for service state parametrization
        return service
    return _service_db_user_not_id_db


@pytest.fixture
def service_db_user_with_invalid_pass(service: AuthService):
    """
    Возвращает функцию для создания сервиса.

    Возвращаемая функция примает username и password,
    создает запись о пользователе в базе данных.
    При этом созданный пользователь имеет хэш пароля
    не соответствующий переданному паролю.

    :param service: экземпляр сервиса
    :type service: AuthService
    :return: функция создания сервиса
    :rtype: callable
    """
    async def _service_db_user_with_invalid_pass(username, password):  # noqa: WPS430, E501 need for service state parametrization
        user_id = 1
        invalid_password = 'invalid_password'  # noqa: S105 test pass
        user = User(
            username=username,
            password_hash=service.hash.get(invalid_password),
            user_id=user_id,
        )
        await service.repository.create_user(user)
        return service
    return _service_db_user_with_invalid_pass


@pytest.fixture
def service_db_token_not_found(service: AuthService):
    """
    Возвращает функцию для создания сервиса.

    Возвращаемая функция примает username и password,
    создает запись о пользователе в базе данных
    и добавляет токен для пользователя в базу данных.

    :param service: экземпляр сервиса
    :type service: AuthService
    :return: функция создания сервиса
    :rtype: callable
    """
    async def _service_db_token_not_found(username, password):  # noqa: WPS430, E501 need for service state parametrization
        user_id = 1
        user = User(
            username=username,
            password_hash=service.hash.get(password),
            user_id=user_id,
        )
        token = service.encoder.encode(user)
        return service, token
    return _service_db_token_not_found


@pytest.fixture
def service_db_token_found(service: AuthService):
    """
    Возвращает функцию для создания сервиса.

    Возвращаемая функция примает username и password,
    создает запись о пользователе в базе данных
    и добавляет токен для пользователя в базу данных.

    :param service: экземпляр сервиса
    :type service: AuthService
    :return: функция создания сервиса
    :rtype: callable
    """
    async def _service_db_token_found(username, password):  # noqa: WPS430, E501 need for service state parametrization
        user_id = 1
        user = User(
            username=username,
            password_hash=service.hash.get(password),
            user_id=user_id,
        )
        token = service.encoder.encode(user)
        await service.cache.create_cache(token)
        return service, token
    return _service_db_token_found


@pytest.fixture
def service_mocker(monkeypatch):
    """
    Мокирует app.api.handlers.service, возращает функцию мокирования.

    Функция мокирования принимает объект сервиса и подменяет им
    объект сервиса в модуле хэндлеров.

    :param monkeypatch: Фикстура для патча объектов
    :return: Функция мокирования
    :rtype: Callable
    """
    def _service_mocker(service: AuthService):  # noqa: WPS430 need for params
        monkeypatch.setattr(
            'app.service.app.service',
            service,
        )
    return _service_mocker
