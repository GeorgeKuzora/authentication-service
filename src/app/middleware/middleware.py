import logging
import time

from fastapi import Request, status

from app.core.interfaces import MetricsClient
from app.metrics.metrics import AuthStatus, NoneClient

logger = logging.getLogger(__name__)


service_name = 'auth-service'


def get_metrics_client_from_request(request: Request) -> MetricsClient:
    """Получает клиент метрик из запроса."""
    try:
        return request.state.metrics_client
    except Exception:
        logger.error('expected MetricsCLient but received None')
        return NoneClient()


async def ready_metric_middleware(request: Request, call_next):
    """Middleware для сбора метрики READY_COUNT."""
    metrics_client = get_metrics_client_from_request(request)
    response = await call_next(request)

    path = request.url.path
    if path.startswith('/healthz/ready'):
        metrics_client.inc_ready_count(
            method=request.method,
            service=service_name,
            endpoint=path,
            status=response.status_code,
        )
    return response


async def duration_metric_middleware(request: Request, call_next):
    """Middleware для сбора метрики REQUEST_DURATION."""
    metrics_client = get_metrics_client_from_request(request)
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    metrics_client.observe_duration(
        process_time=process_time,
        method=request.method,
        service=service_name,
        endpoint=request.url.path,
    )
    return response


async def count_metric_middleware(request: Request, call_next):
    """Middleware для сбора метрики REQUEST_COUNT."""
    metrics_client = get_metrics_client_from_request(request)
    response = await call_next(request)

    metrics_client.inc_request_count(
        method=request.method,
        service=service_name,
        endpoint=request.url.path,
        status=response.status_code,
    )
    return response


async def auth_metric_middleware(request: Request, call_next):
    """Middleware для сбора метрики AUTH_COUNT."""
    metrics_client = get_metrics_client_from_request(request)
    response = await call_next(request)
    response_status_code = response.status_code

    if response_status_code == status.HTTP_200_OK:
        auth_status = AuthStatus.success
    else:
        auth_status = AuthStatus.failure

    metrics_client.observe_auth(
        auth_status=auth_status,
        method=request.method,
        service=service_name,
        endpoint=request.url.path,
        status=response.status_code,
    )
    return response
