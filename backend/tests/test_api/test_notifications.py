import pytest
from httpx import ASGITransport, AsyncClient

from app.config import settings
from app.main import app


async def _get_status() -> dict:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        r = await c.get("/api/v1/notifications/channels-status")
        assert r.status_code == 200
        return r.json()


@pytest.mark.asyncio
async def test_channels_status_booleans_only():
    data = await _get_status()
    assert set(data) == {"web_push_ready", "smtp_ready"}
    assert all(isinstance(v, bool) for v in data.values())
    # default settings have no VAPID and smtp_host == "localhost"
    assert data["web_push_ready"] is False
    assert data["smtp_ready"] is False


@pytest.mark.asyncio
async def test_channels_status_reflects_config(monkeypatch):
    monkeypatch.setattr(settings, "vapid_public_key", "pub")
    monkeypatch.setattr(settings, "vapid_private_key", "priv")
    monkeypatch.setattr(settings, "smtp_host", "mail.real.example")
    data = await _get_status()
    assert data == {"web_push_ready": True, "smtp_ready": True}


@pytest.mark.asyncio
async def test_template_placeholder_smtp_counts_unconfigured(monkeypatch):
    # .env.example ships SMTP_HOST=smtp.example.com; a fresh deploy must not
    # see the readiness chip claim email is usable.
    monkeypatch.setattr(settings, "smtp_host", "smtp.example.com")
    data = await _get_status()
    assert data["smtp_ready"] is False
