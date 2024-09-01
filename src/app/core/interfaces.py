from typing import Protocol


class MetricsClient(Protocol):
    """Интерфейс клиента сбора метрик."""

    def inc_ready_count(self, **kwargs) -> None:
        """Метод подчета вызовов пробы healthz/ready."""
        ...

    def inc_request_count(self, **kwargs) -> None:
        """Метод подчета вызовов."""
        ...

    def observe_duration(self, *, process_time, **kwargs) -> None:
        """Метод сбора метрик о продолжительности вызова."""
        ...

    def observe_auth(self, *, auth_status, **kwargs) -> None:
        """Метод сбора метрик о попытках регистрации."""
        ...
