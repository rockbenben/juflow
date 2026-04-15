import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_group(client: AsyncClient, auth_headers):
    resp = await client.post("/api/groups/", json={"name": "财经投资", "icon": "📈"}, headers=auth_headers)
    assert resp.status_code == 201
    assert resp.json()["name"] == "财经投资"


@pytest.mark.asyncio
async def test_list_groups(client: AsyncClient, auth_headers):
    await client.post("/api/groups/", json={"name": "G1"}, headers=auth_headers)
    resp = await client.get("/api/groups/", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


@pytest.mark.asyncio
async def test_update_group(client: AsyncClient, auth_headers):
    create = await client.post("/api/groups/", json={"name": "Old"}, headers=auth_headers)
    gid = create.json()["id"]
    resp = await client.put(f"/api/groups/{gid}", json={"name": "New"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "New"


@pytest.mark.asyncio
async def test_delete_group(client: AsyncClient, auth_headers):
    create = await client.post("/api/groups/", json={"name": "ToDelete"}, headers=auth_headers)
    gid = create.json()["id"]
    resp = await client.delete(f"/api/groups/{gid}", headers=auth_headers)
    assert resp.status_code == 204
