from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession
from app.crud import user as user_crud
from app.schemas.user import UserCreate, UserPublic

router = APIRouter()


@router.get("/", response_model=list[UserPublic])
async def list_users(db: DbSession) -> list[UserPublic]:
    users = await user_crud.list_users(db)
    return [UserPublic.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserPublic)
async def get_user(user_id: int, db: DbSession) -> UserPublic:
    user = await user_crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserPublic.model_validate(user)


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
async def create_user(payload: UserCreate, db: DbSession) -> UserPublic:
    exists = await user_crud.get_user_by_email(db, str(payload.email))
    if exists is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = await user_crud.create_user(db, payload)
    return UserPublic.model_validate(user)


@router.put("/{user_id}", response_model=UserPublic)
async def replace_user(user_id: int, payload: UserCreate, db: DbSession) -> UserPublic:
    user = await user_crud.replace_user(db, user_id, payload)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return UserPublic.model_validate(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db: DbSession) -> None:
    if not await user_crud.delete_user(db, user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
