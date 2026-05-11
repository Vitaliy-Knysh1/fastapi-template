"""Populate the database with demo catalog and optional sample users (run after migrations)."""

from __future__ import annotations

import asyncio
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/app")

from app.core.config import settings  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.crud import game as game_crud  # noqa: E402
from app.crud import genre as genre_crud  # noqa: E402
from app.crud import order as order_crud  # noqa: E402
from app.crud import order_line as line_crud  # noqa: E402
from app.crud import profile as profile_crud  # noqa: E402
from app.crud import user as user_crud  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.schemas.game import GameCreate  # noqa: E402
from app.schemas.genre import GenreCreate  # noqa: E402
from app.schemas.order import OrderCreate  # noqa: E402
from app.schemas.order_line import OrderLineCreate  # noqa: E402
from app.schemas.profile import ProfileCreate  # noqa: E402

STOREFRONT_SPECS: list[dict[str, object]] = [
    {
        "slug": "balatro",
        "title": "Balatro",
        "genre_name": "Roguelike",
        "genre_slug": "roguelike",
        "description": "Poker-inspired roguelike deckbuilder with wild synergies and endless runs.",
        "price_uah": 325,
        "thumbnail_path": "images/games/balatro.png",
        "tags": ["Deckbuilder", "Indie"],
        "stock": 80,
    },
    {
        "slug": "geometry-dash",
        "title": "Geometry Dash",
        "genre_name": "Rhythm",
        "genre_slug": "rhythm",
        "description": "Rhythm-based platformer — jump, fly, and crash through iconic levels to the beat.",
        "price_uah": 124,
        "thumbnail_path": "images/games/geometry_dash.png",
        "tags": ["Platformer", "Rhythm", "Indie"],
        "stock": 200,
    },
    {
        "slug": "monster-hunter-world",
        "title": "Monster Hunter: World",
        "genre_name": "Action",
        "genre_slug": "action",
        "description": "Team up and hunt massive beasts in sprawling ecosystems with deep weapon mastery.",
        "price_uah": 949,
        "thumbnail_path": "images/games/mh_world.png",
        "tags": ["Co-op", "Action RPG", "Hunting"],
        "stock": 60,
    },
    {
        "slug": "persona-3-reload",
        "title": "Persona 3 Reload",
        "genre_name": "JRPG",
        "genre_slug": "jrpg",
        "description": "Rebuild of a classic — school life by day, dungeon-crawling with Personas by night.",
        "price_uah": 1799,
        "thumbnail_path": "images/games/persona3.png",
        "tags": ["JRPG", "Turn-based", "Narrative"],
        "stock": 45,
    },
    {
        "slug": "persona-4-golden",
        "title": "Persona 4 Golden",
        "genre_name": "JRPG",
        "genre_slug": "jrpg",
        "description": "Investigate a rural mystery, forge bonds, and dive into the TV world.",
        "price_uah": 649,
        "thumbnail_path": "images/games/persona4.png",
        "tags": ["JRPG", "Turn-based", "Narrative"],
        "stock": 55,
    },
    {
        "slug": "clair-obscur-expedition-33",
        "title": "Clair Obscur: Expedition 33",
        "genre_name": "RPG",
        "genre_slug": "rpg",
        "description": "Art-driven turn-based RPG with a haunting world and expedition beyond the unknown.",
        "price_uah": 1499,
        "thumbnail_path": "images/games/expedition_33.png",
        "tags": ["Turn-based", "Narrative", "French RPG", "Indie"],
        "stock": 40,
    },
    {
        "slug": "hollow-knight-silksong",
        "title": "Hollow Knight: Silksong",
        "genre_name": "Metroidvania",
        "genre_slug": "metroidvania",
        "description": "Play as Hornet in a vast new kingdom of silk, song, and precision combat.",
        "price_uah": 415,
        "thumbnail_path": "images/games/silksong.png",
        "tags": ["Metroidvania", "Indie", "Platformer"],
        "stock": 120,
    },
    {
        "slug": "minecraft",
        "title": "Minecraft",
        "genre_name": "Sandbox",
        "genre_slug": "sandbox",
        "description": "Build, mine, and survive in infinite blocky worlds alone or with friends.",
        "price_uah": 2302,
        "thumbnail_path": "images/games/minecraft.png",
        "tags": ["Sandbox", "Survival", "Creative"],
        "stock": 999,
    },
]


async def upsert_storefront_catalog(db) -> None:
    for spec in STOREFRONT_SPECS:
        genre = await genre_crud.get_genre_by_slug(db, str(spec["genre_slug"]))
        if genre is None:
            genre = await genre_crud.create_genre(
                db,
                GenreCreate(name=str(spec["genre_name"]), slug=str(spec["genre_slug"])),
            )
        tags_json = json.dumps(spec["tags"])
        price_uah = int(spec["price_uah"])
        price_cents = price_uah * 100
        existing = await game_crud.get_game_by_slug(db, str(spec["slug"]))
        if existing is not None:
            existing.genre_id = genre.id
            existing.title = str(spec["title"])
            existing.slug = str(spec["slug"])
            existing.description = str(spec["description"])
            existing.price_cents = price_cents
            existing.stock = int(spec["stock"])
            existing.thumbnail_path = str(spec["thumbnail_path"])
            existing.price_uah = price_uah
            existing.tags_json = tags_json
            await db.flush()
            await db.refresh(existing)
        else:
            payload = GameCreate(
                genre_id=genre.id,
                title=str(spec["title"]),
                slug=str(spec["slug"]),
                description=str(spec["description"]),
                price_cents=price_cents,
                stock=int(spec["stock"]),
                thumbnail_path=str(spec["thumbnail_path"]),
                price_uah=price_uah,
                tags_json=tags_json,
            )
            await game_crud.create_game(db, payload)


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        async with db.begin():
            await upsert_storefront_catalog(db)

    async with AsyncSessionLocal() as db:
        if await user_crud.get_user_by_email(db, "alice@example.com") is not None:
            print(
                "Seed skipped: sample users already exist (alice@example.com). "
                "Storefront catalog was updated. Use a fresh DB to re-seed users and orders.",
            )
            return

    async with AsyncSessionLocal() as db:
        async with db.begin():
            u1 = await user_crud.create_user_with_password(
                db,
                email="alice@example.com",
                name="Alice Player",
                password_hash=hash_password("alicepass123"),
            )
            u2 = await user_crud.create_user_with_password(
                db,
                email="bob@example.com",
                name="Bob Speedrun",
                password_hash=hash_password("bobpass123"),
            )
            await profile_crud.create_profile(
                db,
                ProfileCreate(user_id=u1.id, display_name="Alice", bio="Loves RPGs", country="UA"),
            )
            await profile_crud.create_profile(
                db,
                ProfileCreate(user_id=u2.id, display_name="Bob", bio="Roguelike fan", country="PL"),
            )
            games = await game_crud.list_games(db)
            gid = {g.slug: g.id for g in games}
            order1 = await order_crud.create_order(db, OrderCreate(user_id=u1.id))
            order2 = await order_crud.create_order(db, OrderCreate(user_id=u2.id, status="paid"))
            await line_crud.create_order_line(
                db,
                OrderLineCreate(
                    order_id=order1.id,
                    game_id=gid["balatro"],
                    quantity=1,
                    unit_price_cents=32500,
                    wheel_adjustment_cents=0,
                ),
            )
            await line_crud.create_order_line(
                db,
                OrderLineCreate(
                    order_id=order2.id,
                    game_id=gid["persona-3-reload"],
                    quantity=1,
                    unit_price_cents=179900,
                    wheel_adjustment_cents=0,
                ),
            )
            await line_crud.create_order_line(
                db,
                OrderLineCreate(
                    order_id=order2.id,
                    game_id=gid["geometry-dash"],
                    quantity=2,
                    unit_price_cents=12400,
                    wheel_adjustment_cents=0,
                ),
            )
    print("Seed complete for:", settings.database_url)


if __name__ == "__main__":
    if sys.platform == "win32":
        import selectors

        asyncio.run(
            seed(),
            loop_factory=lambda: asyncio.SelectorEventLoop(selectors.SelectSelector()),
        )
    else:
        asyncio.run(seed())
