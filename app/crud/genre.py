from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.genre import Genre
from app.schemas.genre import GenreCreate, GenreUpdate


async def create_genre(db: AsyncSession, payload: GenreCreate) -> Genre:
    genre = Genre(**payload.model_dump())
    db.add(genre)
    await db.flush()
    await db.refresh(genre)
    return genre


async def get_genre(db: AsyncSession, genre_id: int) -> Genre | None:
    return await db.get(Genre, genre_id)


async def get_genre_by_slug(db: AsyncSession, slug: str) -> Genre | None:
    result = await db.execute(select(Genre).where(Genre.slug == slug))
    return result.scalar_one_or_none()


async def list_genres(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Genre]:
    result = await db.execute(select(Genre).offset(skip).limit(limit).order_by(Genre.id))
    return list(result.scalars().all())


async def replace_genre(db: AsyncSession, genre_id: int, payload: GenreCreate) -> Genre | None:
    genre = await get_genre(db, genre_id)
    if genre is None:
        return None
    genre.name = payload.name
    genre.slug = payload.slug
    await db.flush()
    await db.refresh(genre)
    return genre


async def update_genre(db: AsyncSession, genre_id: int, payload: GenreUpdate) -> Genre | None:
    genre = await get_genre(db, genre_id)
    if genre is None:
        return None
    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(genre, key, val)
    await db.flush()
    await db.refresh(genre)
    return genre


async def delete_genre(db: AsyncSession, genre_id: int) -> bool:
    genre = await get_genre(db, genre_id)
    if genre is None:
        return False
    await db.delete(genre)
    await db.flush()
    return True
