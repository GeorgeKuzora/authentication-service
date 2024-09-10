import logging
from enum import StrEnum
from typing import Final

from prometheus_client import Counter, Histogram

from app.core.config.config import get_settings

logger = logging.getLogger(__name__)


class Label(StrEnum):
    """Названия лэйблов."""

    method = 'method'
    service = 'service'
    endpoint = 'endpoint'
    status = 'status'


class AuthStatus(StrEnum):
    """Имя статуса регистрации."""

    success = 'success'
    failure = 'failure'


SERVICE_PREFIX: Final[str] = get_settings().metrics.service_prefix


class NoneClient:
    """Клиент заглушка сбора метрик."""

    def __init__(self, metrics_app=None) -> None:
        """
        Метод инициализации.

        :param metrics_app: Клиент метрик.
        """
        self.app = metrics_app

    def inc_ready_count(self, **kwargs) -> None:
        """
        Метод подсчета вызовов пробы healthz/ready.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        """
        method_name = self.inc_ready_count.__name__
        logger.debug(method_name)

    def inc_request_count(self, **kwargs) -> None:
        """
        Метод подсчета вызовов.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        """
        method_name = self.inc_request_count.__name__
        logger.debug(method_name)

    def observe_duration(self, *, process_time, **kwargs) -> None:
        """
        Метод сбора метрик о продолжительности вызова.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        :param process_time: Время обработки запроса.
        """
        method_name = self.observe_duration.__name__
        logger.debug(method_name)

    def observe_auth(self, *, auth_status, **kwargs) -> None:
        """
        Метод сбора метрик о попытках регистрации.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        :param auth_status: Статус аутентификации пользователя.
        """
        method_name = self.observe_auth.__name__
        logger.debug(method_name)


class PrometheusClient:
    """Клиент сбора метрик prometheus."""

    def __init__(self, metrics_app) -> None:
        """
        Метод инициализации.

        :param metrics_app: Клиент метрик.
        """
        self.app = metrics_app
        self.ready_count = Counter(
            name=f'{SERVICE_PREFIX}_ready_count',
            documentation='Total number of requests',
            labelnames=[
                Label.method, Label.service, Label.endpoint, Label.status,
            ],
        )
        self.request_count = Counter(
            name=f'{SERVICE_PREFIX}_request_count',
            documentation='Total number of requests',
            labelnames=[
                Label.method, Label.service, Label.endpoint, Label.status,
            ],
        )
        self.request_duration = Histogram(
            name=f'{SERVICE_PREFIX}_request_duration',
            documentation='Time spent processing request',
            labelnames=[Label.method, Label.service, Label.endpoint],
            buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10),
        )
        self.auth_success_count = Counter(
            name=f'{SERVICE_PREFIX}_auth_success_count',
            documentation='Total number of successful authentication requests',
            labelnames=[
                Label.method, Label.service, Label.endpoint, Label.status,
            ],
        )
        self.auth_failure_count = Counter(
            name=f'{SERVICE_PREFIX}_auth_failure_count',
            documentation='Total number of failed authentication requests',
            labelnames=[
                Label.method, Label.service, Label.endpoint, Label.status,
            ],
        )

    def inc_ready_count(self, **kwargs) -> None:
        """
        Метод подсчета вызовов пробы healthz/ready.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        """
        self.ready_count.labels(**kwargs).inc()

    def inc_request_count(self, **kwargs) -> None:
        """
        Метод подсчета вызовов.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        """
        self.request_count.labels(**kwargs).inc()

    def observe_duration(self, *, process_time, **kwargs) -> None:
        """
        Метод сбора метрик о продолжительности вызова.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        :param process_time: Время обработки запроса.
        """
        self.request_duration.labels(**kwargs).observe(process_time)

    def observe_auth(self, *, auth_status, **kwargs) -> None:
        """
        Метод сбора метрик о попытках регистрации.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        :param auth_status: Статус аутентификации пользователя.
        """
        match auth_status:
            case AuthStatus.success:
                self.auth_success_count.labels(**kwargs).inc()
            case AuthStatus.failure:
                self.auth_failure_count.labels(**kwargs).inc()
            case _:
                logger.error(f'undefined AuthStatus {auth_status}')
