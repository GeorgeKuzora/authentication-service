from typing import Protocol


class MetricsClient(Protocol):
    """Интерфейс клиента сбора метрик."""

    def inc_ready_count(self, **kwargs) -> None:
        """
        Метод подсчета вызовов пробы healthz/ready.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        """
        ...

    def inc_request_count(self, **kwargs) -> None:
        """
        Метод подсчета вызовов.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        """
        ...

    def observe_duration(self, *, process_time, **kwargs) -> None:
        """
        Метод сбора метрик о продолжительности вызова.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        :param process_time: Время обработки запроса.
        """
        ...

    def observe_auth(self, *, auth_status, **kwargs) -> None:
        """
        Метод сбора метрик о попытках регистрации.

        :param kwargs: Пары ключ-значение передаваемые в метрику.
        :param auth_status: Статус аутентификации пользователя.
        """
        ...
