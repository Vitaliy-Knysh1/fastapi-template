from fastapi import APIRouter, HTTPException, status

from app.api.deps import DbSession
from app.crud import genre as genre_crud
from app.schemas.genre import GenreCreate, GenrePublic, GenreUpdate

router = APIRouter()


@router.get("/", response_model=list[GenrePublic])
async def list_genres(db: DbSession) -> list[GenrePublic]:
    rows = await genre_crud.list_genres(db)
    return [GenrePublic.model_validate(r) for r in rows]


@router.get("/{genre_id}", response_model=GenrePublic)
async def get_genre(genre_id: int, db: DbSession) -> GenrePublic:
    row = await genre_crud.get_genre(db, genre_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    return GenrePublic.model_validate(row)


@router.post("/", response_model=GenrePublic, status_code=status.HTTP_201_CREATED)
async def create_genre(payload: GenreCreate, db: DbSession) -> GenrePublic:
    row = await genre_crud.create_genre(db, payload)
    return GenrePublic.model_validate(row)


@router.put("/{genre_id}", response_model=GenrePublic)
async def replace_genre(genre_id: int, payload: GenreCreate, db: DbSession) -> GenrePublic:
    row = await genre_crud.replace_genre(db, genre_id, payload)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    return GenrePublic.model_validate(row)


@router.patch("/{genre_id}", response_model=GenrePublic)
async def patch_genre(genre_id: int, payload: GenreUpdate, db: DbSession) -> GenrePublic:
    row = await genre_crud.update_genre(db, genre_id, payload)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
    return GenrePublic.model_validate(row)


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(genre_id: int, db: DbSession) -> None:
    if not await genre_crud.delete_genre(db, genre_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Genre not found")
