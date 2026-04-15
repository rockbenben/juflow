import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_subscription_csdn(client: AsyncClient, auth_headers):
    resp = await client.post("/api/subscriptions/", json={
        "url": "https://blog.csdn.net/test_user",
        "fetch_interval": 300,
    }, headers=auth_headers)
    assert resp.status_code == 201
    data = resp.json()
    assert data["source"]["platform"] == "csdn"
    assert data["source"]["platform_uid"] == "test_user"
    assert data["fetch_interval"] == 300


@pytest.mark.asyncio
async def test_create_subscription_xueqiu(client: AsyncClient, auth_headers):
    resp = await client.post("/api/subscriptions/", json={
        "url": "https://xueqiu.com/u/1234567890",
    }, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["source"]["platform"] == "xueqiu"


@pytest.mark.asyncio
async def test_create_subscription_unsupported_url(client: AsyncClient, auth_headers):
    resp = await client.post("/api/subscriptions/", json={
        "url": "https://unknown-platform.com/user",
    }, headers=auth_headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_create_duplicate_subscription(client: AsyncClient, auth_headers):
    await client.post("/api/subscriptions/", json={"url": "https://blog.csdn.net/dup_user"}, headers=auth_headers)
    resp = await client.post("/api/subscriptions/", json={"url": "https://blog.csdn.net/dup_user"}, headers=auth_headers)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_list_subscriptions(client: AsyncClient, auth_headers):
    await client.post("/api/subscriptions/", json={"url": "https://blog.csdn.net/list_user"}, headers=auth_headers)
    resp = await client.get("/api/subscriptions/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_delete_subscription(client: AsyncClient, auth_headers):
    create_resp = await client.post("/api/subscriptions/", json={"url": "https://blog.csdn.net/del_user"}, headers=auth_headers)
    sub_id = create_resp.json()["id"]
    resp = await client.delete(f"/api/subscriptions/{sub_id}", headers=auth_headers)
    assert resp.status_code == 204
