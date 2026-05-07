import json

import pytest

from app.crud import cart as cart_crud
from app.crud import game as game_crud
from app.crud import game_comment as comment_crud
from app.crud import genre as genre_crud
from app.crud import order as order_crud
from app.crud import order_line as line_crud
from app.crud import profile as profile_crud
from app.crud import user as user_crud
from app.schemas.game import GameCreate
from app.schemas.genre import GenreCreate
from app.schemas.order import OrderCreate
from app.schemas.order_line import OrderLineCreate
from app.schemas.profile import ProfileCreate
from app.schemas.user import UserCreate, UserUpdate


@pytest.mark.anyio
async def test_user_crud(db_session):
    u = await user_crud.create_user(db_session, UserCreate(email="a@t.com", name="A"))
    assert u.id
    assert (await user_crud.get_user(db_session, u.id)).email == "a@t.com"
    assert await user_crud.get_user_by_email(db_session, "a@t.com")

    upd = await user_crud.update_user(db_session, u.id, UserUpdate(name="B"))
    assert upd.name == "B"

    lst = await user_crud.list_users(db_session)
    assert len(lst) == 1

    assert await user_crud.delete_user(db_session, u.id)
    assert await user_crud.get_user(db_session, u.id) is None


@pytest.mark.anyio
async def test_profile_crud(db_session):
    u = await user_crud.create_user(db_session, UserCreate(email="p@t.com", name="P"))
    p = await profile_crud.create_profile(db_session, ProfileCreate(user_id=u.id, display_name="Nick"))
    assert p.id
    assert (await profile_crud.get_profile_by_user(db_session, u.id)).id == p.id
    assert (await profile_crud.list_profiles(db_session))[0].id == p.id
    assert await profile_crud.delete_profile(db_session, p.id)


@pytest.mark.anyio
async def test_genre_and_game_crud(db_session):
    genre = await genre_crud.create_genre(db_session, GenreCreate(name="RPG", slug="rpg"))
    assert genre.id
    g = await game_crud.create_game(
        db_session,
        GameCreate(
            genre_id=genre.id,
            title="G",
            slug="g",
            description="d",
            price_cents=100,
            stock=3,
            thumbnail_path="t.png",
            price_uah=1,
            tags_json=json.dumps(["Indie"]),
        ),
    )
    assert g.id
    assert (await game_crud.get_game_by_slug(db_session, "g")).id == g.id
    assert (await game_crud.list_games(db_session))[0].id == g.id
    assert (await game_crud.list_storefront_games(db_session))[0].id == g.id
    assert await game_crud.delete_game(db_session, g.id)


@pytest.mark.anyio
async def test_game_comments_crud(db_session):
    u = await user_crud.create_user(db_session, UserCreate(email="c@t.com", name="C"))
    genre = await genre_crud.create_genre(db_session, GenreCreate(name="Puzzle", slug="puzzle"))
    game = await game_crud.create_game(
        db_session,
        GameCreate(
            genre_id=genre.id,
            title="Balatro",
            slug="balatro",
            description="d",
            price_cents=32500,
            stock=3,
            thumbnail_path="t.png",
            price_uah=325,
            tags_json="[]",
        ),
    )
    c = await comment_crud.create_comment(db_session, game_id=game.id, user_id=u.id, body="Hi")
    rows = await comment_crud.list_for_game_with_authors(db_session, game.id)
    assert rows and rows[0][0].id == c.id


@pytest.mark.anyio
async def test_order_and_order_line_crud(db_session):
    u = await user_crud.create_user(db_session, UserCreate(email="o@t.com", name="O"))
    genre = await genre_crud.create_genre(db_session, GenreCreate(name="Action", slug="action"))
    game = await game_crud.create_game(
        db_session,
        GameCreate(
            genre_id=genre.id,
            title="MH",
            slug="mh",
            description="d",
            price_cents=94900,
            stock=3,
            thumbnail_path="t.png",
            price_uah=949,
            tags_json="[]",
        ),
    )
    order = await order_crud.create_order(db_session, OrderCreate(user_id=u.id))
    line = await line_crud.create_order_line(
        db_session,
        OrderLineCreate(order_id=order.id, game_id=game.id, quantity=2, unit_price_cents=94900, wheel_adjustment_cents=0),
    )
    await order_crud.refresh_order_total(db_session, order.id)
    o = await order_crud.get_order(db_session, order.id)
    assert o.total_cents == 2 * 94900
    assert (await line_crud.get_order_line(db_session, line.id)).id == line.id
    assert len(await line_crud.lines_for_order(db_session, order.id)) == 1
    assert await order_crud.delete_order(db_session, order.id)


@pytest.mark.anyio
async def test_cart_crud(db_session):
    u = await user_crud.create_user(db_session, UserCreate(email="cart@t.com", name="Cart"))
    genre = await genre_crud.create_genre(db_session, GenreCreate(name="Roguelike", slug="roguelike"))
    game = await game_crud.create_game(
        db_session,
        GameCreate(
            genre_id=genre.id,
            title="Balatro",
            slug="balatro",
            description="d",
            price_cents=32500,
            stock=10,
            thumbnail_path="t.png",
            price_uah=325,
            tags_json="[]",
        ),
    )
    await cart_crud.add_item(db_session, u.id, game.id, 1)
    await cart_crud.add_item(db_session, u.id, game.id, 2)
    items = await cart_crud.list_cart_items(db_session, u.id)
    assert items[0].quantity == 3
    assert await cart_crud.cart_item_count(db_session, u.id) == 3
    await cart_crud.set_quantity(db_session, u.id, game.id, 1)
    assert (await cart_crud.list_cart_items(db_session, u.id))[0].quantity == 1
    assert await cart_crud.remove_item(db_session, u.id, game.id)
    assert await cart_crud.cart_item_count(db_session, u.id) == 0

