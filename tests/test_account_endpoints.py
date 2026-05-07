import pytest

from tests.conftest import register_and_login


@pytest.mark.anyio
async def test_account_summary_and_whoami_and_stats(client):
    user = await register_and_login(client, email="acct@test.com")

    r = await client.get("/api/v1/account/summary")
    assert r.status_code == 200
    assert r.json()["id"] == user["id"]

    r = await client.get("/api/v1/account/whoami")
    assert r.status_code == 200
    assert r.json()["id"] == user["id"]

    r = await client.get("/api/v1/account/stats")
    assert r.status_code == 200
    assert r.json()["orders_count"] == 0


@pytest.mark.anyio
async def test_account_requires_auth(client):
    assert (await client.get("/api/v1/account/summary")).status_code == 401
    assert (await client.get("/api/v1/account/whoami")).status_code == 401
    assert (await client.get("/api/v1/account/stats")).status_code == 401

