import pytest


@pytest.mark.anyio
async def test_auth_ping(client):
    r = await client.get("/api/v1/auth/ping")
    assert r.status_code == 200
    assert r.json()["message"] == "auth ok"


@pytest.mark.anyio
async def test_register_login_me_logout(client):
    r = await client.post(
        "/api/v1/auth/register",
        json={"email": "alice@test.com", "name": "Alice", "password": "alicepass123"},
    )
    assert r.status_code == 201
    user = r.json()
    assert user["email"] == "alice@test.com"

    r = await client.post("/api/v1/auth/login", json={"email": "alice@test.com", "password": "alicepass123"})
    assert r.status_code == 200

    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 200
    assert r.json()["email"] == "alice@test.com"

    r = await client.post("/api/v1/auth/logout")
    assert r.status_code == 200

    r = await client.get("/api/v1/auth/me")
    assert r.status_code == 401


@pytest.mark.anyio
async def test_register_duplicate_email_returns_409(client):
    payload = {"email": "dup@test.com", "name": "Dup", "password": "dup123456"}
    r = await client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 201
    r = await client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 409


@pytest.mark.anyio
async def test_login_wrong_password_401(client):
    await client.post(
        "/api/v1/auth/register",
        json={"email": "bob@test.com", "name": "Bob", "password": "bobpass123"},
    )
    r = await client.post("/api/v1/auth/login", json={"email": "bob@test.com", "password": "wrong"})
    assert r.status_code == 401

