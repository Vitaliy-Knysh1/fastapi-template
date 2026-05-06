from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def create_user(db: AsyncSession, payload: UserCreate) -> User:
    user = User(**payload.model_dump())
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def get_user(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def list_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[User]:
    result = await db.execute(select(User).offset(skip).limit(limit).order_by(User.id))
    return list(result.scalars().all())


async def replace_user(db: AsyncSession, user_id: int, payload: UserCreate) -> User | None:
    user = await get_user(db, user_id)
    if user is None:
        return None
    await db.execute(
        update(User)
        .where(User.id == user_id)
        .values(**payload.model_dump()),
    )
    await db.flush()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: int, payload: UserUpdate) -> User | None:
    user = await get_user(db, user_id)
    if user is None:
        return None
    data = payload.model_dump(exclude_unset=True)
    if not data:
        return user
    await db.execute(update(User).where(User.id == user_id).values(**data))
    await db.flush()
    await db.refresh(user)
    return user


async def delete_user(db: AsyncSession, user_id: int) -> bool:
    user = await get_user(db, user_id)
    if user is None:
        return False
    await db.execute(delete(User).where(User.id == user_id))
    return True
