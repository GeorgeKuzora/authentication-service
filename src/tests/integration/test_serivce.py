import pytest

from app.core.authentication import AuthService
from app.metrics.metrics import NoneClient, PrometheusClient
from app.service import app, get_metrics, get_service, lifespan


@pytest.mark.asyncio
async def test_get_serivce():
    """Тестирует функцию get_service."""
    serivce = get_service()

    assert isinstance(serivce, AuthService)


@pytest.mark.asyncio
async def test_get_metrics():
    """Тестирует фунцию get_metrics."""
    metrics = get_metrics(app=None)

    assert isinstance(metrics, (NoneClient, PrometheusClient))


@pytest.mark.asyncio
async def test_lifespan():
    """Тестирует функцию lifespan."""
    res = lifespan(app)
    assert res
