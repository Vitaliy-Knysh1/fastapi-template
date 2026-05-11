import pytest

from tests.conftest import register_and_login


@pytest.mark.anyio
async def test_orders_and_order_lines_basic_crud(client):
    u = await register_and_login(client, email="orders@test.com")

    r = await client.post("/api/v1/orders/", json={"user_id": u["id"], "status": "pending"})
    assert r.status_code == 201
    order_id = r.json()["id"]

    r = await client.get("/api/v1/orders/")
    assert r.status_code == 200
    assert any(x["id"] == order_id for x in r.json())

    r = await client.get("/api/v1/orders/me")
    assert r.status_code == 200
    assert any(x["id"] == order_id for x in r.json())

    g = await client.post("/api/v1/genres/", json={"name": "Action", "slug": "action"})
    genre_id = g.json()["id"]
    game = await client.post(
        "/api/v1/games/",
        json={
            "genre_id": genre_id,
            "title": "Monster Hunter: World",
            "slug": "monster-hunter-world",
            "description": "Test",
            "price_cents": 94900,
            "stock": 10,
            "thumbnail_path": "images/games/mh_world.png",
            "price_uah": 949,
            "tags_json": "[]",
        },
    )
    game_id = game.json()["id"]

    r = await client.post(
        "/api/v1/order-lines/",
        json={
            "order_id": order_id,
            "game_id": game_id,
            "quantity": 2,
            "unit_price_cents": 94900,
            "wheel_adjustment_cents": 0,
        },
    )
    assert r.status_code == 201
    line_id = r.json()["id"]

    r = await client.get(f"/api/v1/order-lines/{line_id}")
    assert r.status_code == 200

    r = await client.get(f"/api/v1/order-lines/order/{order_id}")
    assert r.status_code == 200
    assert len(r.json()) == 1

    r = await client.patch(f"/api/v1/order-lines/{line_id}", json={"quantity": 1})
    assert r.status_code == 200

    r = await client.get(f"/api/v1/orders/{order_id}")
    assert r.status_code == 200
    assert r.json()["lines"][0]["id"] == line_id

    r = await client.delete(f"/api/v1/order-lines/{line_id}")
    assert r.status_code == 204

    r = await client.delete(f"/api/v1/orders/{order_id}")
    assert r.status_code == 204


@pytest.mark.anyio
async def test_cart_and_checkout_flow(client, monkeypatch):
    await register_and_login(client, email="checkout@test.com")

    g = await client.post("/api/v1/genres/", json={"name": "Roguelike", "slug": "roguelike"})
    genre_id = g.json()["id"]
    game = await client.post(
        "/api/v1/games/",
        json={
            "genre_id": genre_id,
            "title": "Balatro",
            "slug": "balatro",
            "description": "Test",
            "price_cents": 32500,
            "stock": 5,
            "thumbnail_path": "images/games/balatro.png",
            "price_uah": 325,
            "tags_json": "[]",
        },
    )
    game_id = game.json()["id"]

    r = await client.post("/api/v1/cart/items", json={"game_id": game_id, "quantity": 2})
    assert r.status_code == 201
    assert r.json()["item_count"] == 2

    r = await client.get("/api/v1/cart")
    assert r.status_code == 200
    assert r.json()["subtotal_uah"] == 650

    import app.api.v1.routes.commerce.checkout as checkout_mod

    monkeypatch.setattr(checkout_mod.random, "random", lambda: 0.1)

    r = await client.post(
        "/api/v1/checkout/complete",
        json={
            "full_name": "Tester",
            "email": "checkout@test.com",
            "phone": "12345",
            "address_line1": "Street 1",
            "city": "Kyiv",
            "postal_code": "01001",
            "country": "UA",
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert data["lines"][0]["title"] == "Balatro"
    assert data["lines"][0]["adjustment_uah_per_unit"] == -1
    assert data["total_uah"] == 648.0

    r = await client.get("/api/v1/cart")
    assert r.status_code == 200
    assert r.json()["item_count"] == 0
