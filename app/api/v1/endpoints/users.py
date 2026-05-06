from fastapi import APIRouter, HTTPException, status

from app.crud.crud_user import crud_user
from app.schemas.user import UserCreate, UserPublic

router = APIRouter()


@router.get("/", response_model=list[UserPublic])
def list_users() -> list[UserPublic]:
    return crud_user.get_multi()


@router.get("/{user_id}", response_model=UserPublic)
def get_user(user_id: int) -> UserPublic:
    user = crud_user.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.post("/", response_model=UserPublic, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate) -> UserPublic:
    return crud_user.create(payload)


@router.put("/{user_id}", response_model=UserPublic)
def replace_user(user_id: int, payload: UserCreate) -> UserPublic:
    user = crud_user.replace(user_id, payload)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> None:
    if not crud_user.delete(user_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
