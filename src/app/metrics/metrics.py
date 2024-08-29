import logging
from enum import StrEnum
from typing import Final

from prometheus_client import Counter, Histogram, make_asgi_app

from app.core.config.config import get_settings

logger = logging.getLogger(__name__)

app = make_asgi_app()


class Label(StrEnum):
    """Названия лэйблов."""

    method = 'method'
    service = 'service'
    endpoint = 'endpoint'
    status = 'status'


class AuthStatus:
    """Имя статуса регистрации."""

    success = 'success'
    failure = 'failure'


SERVICE_PREFIX: Final[str] = get_settings().metrics.service_prefix


class NoneClient:
    """Клиент заглушка сбора метрик."""

    def __init__(self) -> None:
        """Метод инициализации."""
        self.app = None

    def inc_ready_count(self, **kwargs) -> None:
        """Метод подчета вызовов пробы healthz/ready."""
        method_name = self.inc_ready_count.__name__
        logger.debug(method_name)

    def inc_request_count(self, **kwargs) -> None:
        """Метод подчета вызовов."""
        method_name = self.inc_request_count.__name__
        logger.debug(method_name)

    def observe_duration(self, *, process_time, **kwargs) -> None:
        """Метод сбора метрик о продолжительности вызова."""
        method_name = self.observe_duration.__name__
        logger.debug(method_name)

    def observe_auth(self, *, auth_status, **kwargs) -> None:
        """Метод сбора метрик о попытках регистрации."""
        method_name = self.observe_auth.__name__
        logger.debug(method_name)


class PrometheusClient:
    """Клиент сбора метрик prometheus."""

    def __init__(self) -> None:
        """Метод инициализации."""
        self.app = app
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
            documentation='Total number of successfull authentication requests',
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
        """Метод подчета вызовов пробы healthz/ready."""
        self.ready_count.labels(**kwargs).inc()

    def inc_request_count(self, **kwargs) -> None:
        """Метод подчета вызовов."""
        self.request_count.labels(**kwargs).inc()

    def observe_duration(self, *, process_time, **kwargs) -> None:
        """Метод сбора метрик о продолжительности вызова."""
        self.request_duration.labels(**kwargs).observe(process_time)

    def observe_auth(self, *, auth_status, **kwargs) -> None:
        """Метод сбора метрик о попытках регистрации."""
        match auth_status:
            case AuthStatus.success:
                self.auth_success_count.labels(**kwargs).inc()
            case AuthStatus.failure:
                self.auth_failure_count.labels(**kwargs).inc()
            case _:
                logger.error(f'undefined AuthStatus {auth_status}')
