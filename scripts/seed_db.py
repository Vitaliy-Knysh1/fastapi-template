"""
Load sample data into all tables (async). Run after migrations.

  set DATABASE_URL=postgresql://postgres:postgres@localhost:5432/app
  python scripts/seed_db.py

On Windows, the default ProactorEventLoop breaks async psycopg; this script uses a
selector-based loop for `asyncio.run` (see Python 3.12+ `loop_factory`).
"""

from __future__ import annotations

import asyncio
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


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        if await user_crud.get_user_by_email(db, "alice@example.com") is not None:
            print(
                "Seed skipped: sample data already exists (alice@example.com). "
                "Use a fresh DB or delete rows if you need to re-seed.",
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
            g_action = await genre_crud.create_genre(db, GenreCreate(name="Action", slug="action"))
            g_rpg = await genre_crud.create_genre(db, GenreCreate(name="RPG", slug="rpg"))
            g_puzzle = await genre_crud.create_genre(db, GenreCreate(name="Puzzle", slug="puzzle"))
            await game_crud.create_game(
                db,
                GameCreate(
                    genre_id=g_action.id,
                    title="Neon Striker",
                    slug="neon-striker",
                    description="Fast arcade action.",
                    price_cents=2999,
                    stock=50,
                ),
            )
            await game_crud.create_game(
                db,
                GameCreate(
                    genre_id=g_rpg.id,
                    title="Quest of Aether",
                    slug="quest-of-aether",
                    description="Epic single-player RPG.",
                    price_cents=4999,
                    stock=30,
                ),
            )
            await game_crud.create_game(
                db,
                GameCreate(
                    genre_id=g_puzzle.id,
                    title="Blockfold",
                    slug="blockfold",
                    description="Relaxing spatial puzzles.",
                    price_cents=999,
                    stock=100,
                ),
            )
            games = await game_crud.list_games(db)
            gid = {g.slug: g.id for g in games}
            order1 = await order_crud.create_order(db, OrderCreate(user_id=u1.id))
            order2 = await order_crud.create_order(db, OrderCreate(user_id=u2.id, status="paid"))
            await line_crud.create_order_line(
                db,
                OrderLineCreate(
                    order_id=order1.id,
                    game_id=gid["neon-striker"],
                    quantity=1,
                    unit_price_cents=2999,
                    wheel_adjustment_cents=-1,
                ),
            )
            await line_crud.create_order_line(
                db,
                OrderLineCreate(
                    order_id=order2.id,
                    game_id=gid["quest-of-aether"],
                    quantity=1,
                    unit_price_cents=4999,
                    wheel_adjustment_cents=1,
                ),
            )
            await line_crud.create_order_line(
                db,
                OrderLineCreate(
                    order_id=order2.id,
                    game_id=gid["blockfold"],
                    quantity=2,
                    unit_price_cents=999,
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
