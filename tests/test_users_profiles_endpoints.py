import pytest

from tests.conftest import register_and_login


@pytest.mark.anyio
async def test_users_me_and_list_and_get(client):
    u = await register_and_login(client, email="u@test.com")

    r = await client.get("/api/v1/users/me")
    assert r.status_code == 200
    assert r.json()["id"] == u["id"]

    r = await client.get("/api/v1/users/")
    assert r.status_code == 200
    assert any(x["id"] == u["id"] for x in r.json())

    r = await client.get(f"/api/v1/users/{u['id']}")
    assert r.status_code == 200


@pytest.mark.anyio
async def test_users_update_me(client):
    await register_and_login(client, email="patchme@test.com")
    r = await client.patch("/api/v1/users/me", json={"name": "New Name"})
    assert r.status_code == 200
    assert r.json()["name"] == "New Name"


@pytest.mark.anyio
async def test_profiles_crud(client):
    u = await register_and_login(client, email="profile@test.com")

    r = await client.post(
        "/api/v1/profiles/",
        json={"user_id": u["id"], "display_name": "Nick", "bio": "Hello", "country": "UA"},
    )
    assert r.status_code == 201
    pid = r.json()["id"]

    r = await client.get("/api/v1/profiles/")
    assert r.status_code == 200
    assert any(x["id"] == pid for x in r.json())

    r = await client.get(f"/api/v1/profiles/{pid}")
    assert r.status_code == 200

    r = await client.get(f"/api/v1/profiles/by-user/{u['id']}")
    assert r.status_code == 200
    assert r.json()["id"] == pid

    r = await client.patch(f"/api/v1/profiles/{pid}", json={"bio": "Updated"})
    assert r.status_code == 200
    assert r.json()["bio"] == "Updated"

    r = await client.delete(f"/api/v1/profiles/{pid}")
    assert r.status_code == 204


@pytest.mark.anyio
async def test_profiles_duplicate_user_conflict(client):
    u = await register_and_login(client, email="dup_profile@test.com")
    r = await client.post("/api/v1/profiles/", json={"user_id": u["id"], "display_name": "A"})
    assert r.status_code == 201
    r = await client.post("/api/v1/profiles/", json={"user_id": u["id"], "display_name": "B"})
    assert r.status_code == 409

