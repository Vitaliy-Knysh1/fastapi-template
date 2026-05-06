from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game import Game
from app.schemas.game import GameCreate, GameUpdate


async def create_game(db: AsyncSession, payload: GameCreate) -> Game:
    game = Game(**payload.model_dump())
    db.add(game)
    await db.flush()
    await db.refresh(game)
    return game


async def get_game(db: AsyncSession, game_id: int) -> Game | None:
    return await db.get(Game, game_id)


async def list_games(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Game]:
    result = await db.execute(select(Game).offset(skip).limit(limit).order_by(Game.id))
    return list(result.scalars().all())


async def replace_game(db: AsyncSession, game_id: int, payload: GameCreate) -> Game | None:
    game = await get_game(db, game_id)
    if game is None:
        return None
    data = payload.model_dump()
    game.genre_id = data["genre_id"]
    game.title = data["title"]
    game.slug = data["slug"]
    game.description = data["description"]
    game.price_cents = data["price_cents"]
    game.stock = data["stock"]
    await db.flush()
    await db.refresh(game)
    return game


async def update_game(db: AsyncSession, game_id: int, payload: GameUpdate) -> Game | None:
    game = await get_game(db, game_id)
    if game is None:
        return None
    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(game, key, val)
    await db.flush()
    await db.refresh(game)
    return game


async def delete_game(db: AsyncSession, game_id: int) -> bool:
    game = await get_game(db, game_id)
    if game is None:
        return False
    db.delete(game)
    await db.flush()
    return True
