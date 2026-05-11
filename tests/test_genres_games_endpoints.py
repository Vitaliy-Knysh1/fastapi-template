import pytest

from tests.conftest import register_and_login


@pytest.mark.anyio
async def test_genres_crud(client):
    r = await client.post("/api/v1/genres/", json={"name": "RPG", "slug": "rpg"})
    assert r.status_code == 201
    gid = r.json()["id"]

    r = await client.get("/api/v1/genres/")
    assert r.status_code == 200
    assert any(x["id"] == gid for x in r.json())

    r = await client.get(f"/api/v1/genres/{gid}")
    assert r.status_code == 200

    r = await client.patch(f"/api/v1/genres/{gid}", json={"name": "Roleplaying"})
    assert r.status_code == 200
    assert r.json()["name"] == "Roleplaying"

    r = await client.delete(f"/api/v1/genres/{gid}")
    assert r.status_code == 204

    r = await client.get(f"/api/v1/genres/{gid}")
    assert r.status_code == 404


@pytest.mark.anyio
async def test_games_crud_and_by_slug(client):
    g = await client.post("/api/v1/genres/", json={"name": "JRPG", "slug": "jrpg"})
    genre_id = g.json()["id"]

    r = await client.post(
        "/api/v1/games/",
        json={
            "genre_id": genre_id,
            "title": "Persona 4 Golden",
            "slug": "persona-4-golden",
            "description": "Test",
            "price_cents": 64900,
            "stock": 5,
            "thumbnail_path": "images/games/persona4.png",
            "price_uah": 649,
            "tags_json": "[\"JRPG\"]",
        },
    )
    assert r.status_code == 201
    game_id = r.json()["id"]

    r = await client.get("/api/v1/games/")
    assert r.status_code == 200
    assert any(x["id"] == game_id for x in r.json())

    r = await client.get(f"/api/v1/games/{game_id}")
    assert r.status_code == 200

    r = await client.get("/api/v1/games/by-slug/persona-4-golden")
    assert r.status_code == 200
    assert r.json()["genre_name"] == "JRPG"

    r = await client.patch(f"/api/v1/games/{game_id}", json={"stock": 7})
    assert r.status_code == 200
    assert r.json()["stock"] == 7

    r = await client.delete(f"/api/v1/games/{game_id}")
    assert r.status_code == 204


@pytest.mark.anyio
async def test_game_comments_list_and_create(client):
    await register_and_login(client, email="commenter@test.com")
    g = await client.post("/api/v1/genres/", json={"name": "Puzzle", "slug": "puzzle"})
    genre_id = g.json()["id"]
    await client.post(
        "/api/v1/games/",
        json={
            "genre_id": genre_id,
            "title": "Balatro",
            "slug": "balatro",
            "description": "Test",
            "price_cents": 32500,
            "stock": 2,
            "thumbnail_path": "images/games/balatro.png",
            "price_uah": 325,
            "tags_json": "[]",
        },
    )

    r = await client.get("/api/v1/games/by-slug/balatro/comments")
    assert r.status_code == 200
    assert r.json() == []

    r = await client.post("/api/v1/games/by-slug/balatro/comments", json={"body": "Nice!"})
    assert r.status_code == 201
    assert r.json()["body"] == "Nice!"

    r = await client.get("/api/v1/games/by-slug/balatro/comments")
    assert r.status_code == 200
    assert len(r.json()) == 1

