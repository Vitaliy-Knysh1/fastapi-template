from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import Profile
from app.schemas.profile import ProfileCreate, ProfileUpdate


async def create_profile(db: AsyncSession, payload: ProfileCreate) -> Profile:
    profile = Profile(**payload.model_dump())
    db.add(profile)
    await db.flush()
    await db.refresh(profile)
    return profile


async def get_profile(db: AsyncSession, profile_id: int) -> Profile | None:
    return await db.get(Profile, profile_id)


async def get_profile_by_user(db: AsyncSession, user_id: int) -> Profile | None:
    result = await db.execute(select(Profile).where(Profile.user_id == user_id))
    return result.scalar_one_or_none()


async def list_profiles(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Profile]:
    result = await db.execute(select(Profile).offset(skip).limit(limit).order_by(Profile.id))
    return list(result.scalars().all())


async def update_profile(db: AsyncSession, profile_id: int, payload: ProfileUpdate) -> Profile | None:
    profile = await get_profile(db, profile_id)
    if profile is None:
        return None
    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, val)
    await db.flush()
    await db.refresh(profile)
    return profile


async def delete_profile(db: AsyncSession, profile_id: int) -> bool:
    profile = await get_profile(db, profile_id)
    if profile is None:
        return False
    db.delete(profile)
    await db.flush()
    return True
