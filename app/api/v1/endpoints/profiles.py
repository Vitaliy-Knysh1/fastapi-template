from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession
from app.crud import profile as profile_crud
from app.schemas.profile import ProfileCreate, ProfilePublic, ProfileUpdate

router = APIRouter()


@router.get("/", response_model=list[ProfilePublic])
async def list_profiles(db: DbSession) -> list[ProfilePublic]:
    rows = await profile_crud.list_profiles(db)
    return [ProfilePublic.model_validate(r) for r in rows]


@router.get("/by-user/{user_id}", response_model=ProfilePublic)
async def get_profile_for_user(user_id: int, db: DbSession) -> ProfilePublic:
    row = await profile_crud.get_profile_by_user(db, user_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return ProfilePublic.model_validate(row)


@router.get("/{profile_id}", response_model=ProfilePublic)
async def get_profile(profile_id: int, db: DbSession) -> ProfilePublic:
    row = await profile_crud.get_profile(db, profile_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return ProfilePublic.model_validate(row)


@router.post("/", response_model=ProfilePublic, status_code=status.HTTP_201_CREATED)
async def create_profile(payload: ProfileCreate, db: DbSession) -> ProfilePublic:
    exists = await profile_crud.get_profile_by_user(db, payload.user_id)
    if exists is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already has a profile")
    row = await profile_crud.create_profile(db, payload)
    return ProfilePublic.model_validate(row)


@router.patch("/{profile_id}", response_model=ProfilePublic)
async def patch_profile(profile_id: int, payload: ProfileUpdate, db: DbSession) -> ProfilePublic:
    row = await profile_crud.update_profile(db, profile_id, payload)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return ProfilePublic.model_validate(row)


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: int, db: DbSession) -> None:
    if not await profile_crud.delete_profile(db, profile_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
