from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

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


async def list_storefront_games(db: AsyncSession) -> list[Game]:
    result = await db.execute(
        select(Game)
        .where(and_(Game.thumbnail_path.isnot(None), Game.thumbnail_path != ""))
        .order_by(Game.id),
    )
    return list(result.scalars().all())


async def get_game_by_slug(db: AsyncSession, slug: str) -> Game | None:
    result = await db.execute(
        select(Game).options(selectinload(Game.genre)).where(Game.slug == slug),
    )
    return result.scalar_one_or_none()


async def replace_game(db: AsyncSession, game_id: int, payload: GameCreate) -> Game | None:
    game = await get_game(db, game_id)
    if game is None:
        return None
    data = payload.model_dump()
    for key in (
        "genre_id",
        "title",
        "slug",
        "description",
        "price_cents",
        "stock",
        "thumbnail_path",
        "price_uah",
        "tags_json",
    ):
        setattr(game, key, data[key])
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
    await db.delete(game)
    await db.flush()
    return True
