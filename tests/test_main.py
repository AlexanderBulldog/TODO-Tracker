import pytest
from httpx import AsyncClient

from app.main import app

pytestmark = pytest.mark.asyncio


async def test_health_check():
    """Тестирует эндпоинт healthcheck."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_read_root():
    """Тестирует главную страницу."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert "Мой список задач" in response.text
