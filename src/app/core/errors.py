from fastapi import HTTPException, status


class ServerError(HTTPException):
    """Ошибка при проблемах с сервисом."""

    def __init__(
        self,
        status_code: int = status.HTTP_503_SERVICE_UNAVAILABLE,
        detail: str = 'Неизвестная ошибка сервера',
    ):
        """
        Метод инициализации ServerError.

        :param status_code: Код ответа
        :type status_code: int
        :param detail: Сообщение
        :type detail: str
        """
        self.status_code = status_code
        self.detail = detail


class RepositoryError(ServerError):
    """
    Исключение возникающее при запросе в хранилище данных.

    Импортировать в имплементации репозитория данных,
    для вызова исключения при ошибке доступа к данным.
    """


class ConfigError(ServerError):
    """
    Исключение возникающее в ходе конфигурации.

    Импортировать в имплементации репозитория данных,
    для вызова исключения при ошибке доступа к данным.
    """


class CacheError(ServerError):
    """Ошибка в кэше."""


class NotFoundError(Exception):
    """Исключение возникающее когда запрошенная информация не найдена."""

    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        detail: str = 'Запрошенные данные не найдены',
    ):
        """
        Метод инициализации NotFoundError.

        :param status_code: Код ответа
        :type status_code: int
        :param detail: Сообщение
        :type detail: str
        """
        self.status_code = status_code
        self.detail = detail


class AuthorizationError(HTTPException):
    """Исключение возникающее при провале авторизации пользователя."""

    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: str = 'Ошибка авторизации пользователя',
    ):
        """
        Метод инициализации UnauthorizedError.

        :param status_code: Код ответа
        :type status_code: int
        :param detail: Сообщение
        :type detail: str
        """
        self.status_code = status_code
        self.detail = detail


class UnprocessableError(HTTPException):
    """Ошибка при ответе сервера 422."""

    def __init__(
        self,
        status_code: int = status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail: str = 'Запрос имеет неверный формат',
    ):
        """
        Метод инициализации UnprocessableError.

        :param status_code: Код ответа
        :type status_code: int
        :param detail: Сообщение
        :type detail: str
        """
        self.status_code = status_code
        self.detail = detail
