from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.crud import game as game_crud
from app.crud import game_comment as comment_crud
from app.schemas.game import GameCreate, GameDetailPublic, GamePublic, GameUpdate
from app.schemas.game_comment import GameCommentCreate, GameCommentPublic

router = APIRouter()


@router.get("/", response_model=list[GamePublic])
async def list_games(db: DbSession) -> list[GamePublic]:
    rows = await game_crud.list_games(db)
    return [GamePublic.from_game(r) for r in rows]


@router.get("/by-slug/{slug}/comments", response_model=list[GameCommentPublic])
async def list_game_comments(slug: str, db: DbSession) -> list[GameCommentPublic]:
    game = await game_crud.get_game_by_slug(db, slug)
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    rows = await comment_crud.list_for_game_with_authors(db, game.id)
    return [
        GameCommentPublic(
            id=c.id,
            body=c.body,
            created_at=c.created_at,
            author_name=name,
        )
        for c, name in rows
    ]


@router.post(
    "/by-slug/{slug}/comments",
    response_model=GameCommentPublic,
    status_code=status.HTTP_201_CREATED,
)
async def post_game_comment(
    slug: str,
    payload: GameCommentCreate,
    db: DbSession,
    user: CurrentUser,
) -> GameCommentPublic:
    game = await game_crud.get_game_by_slug(db, slug)
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    c = await comment_crud.create_comment(
        db,
        game_id=game.id,
        user_id=user.id,
        body=payload.body,
    )
    return GameCommentPublic(
        id=c.id,
        body=c.body,
        created_at=c.created_at,
        author_name=user.name,
    )


@router.get("/by-slug/{slug}", response_model=GameDetailPublic)
async def get_game_by_slug(slug: str, db: DbSession) -> GameDetailPublic:
    game = await game_crud.get_game_by_slug(db, slug)
    if game is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    base = GamePublic.from_game(game)
    return GameDetailPublic(**base.model_dump(), genre_name=game.genre.name)


@router.get("/{game_id}", response_model=GamePublic)
async def get_game(game_id: int, db: DbSession) -> GamePublic:
    row = await game_crud.get_game(db, game_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return GamePublic.from_game(row)


@router.post("/", response_model=GamePublic, status_code=status.HTTP_201_CREATED)
async def create_game(payload: GameCreate, db: DbSession) -> GamePublic:
    row = await game_crud.create_game(db, payload)
    return GamePublic.from_game(row)


@router.put("/{game_id}", response_model=GamePublic)
async def replace_game(game_id: int, payload: GameCreate, db: DbSession) -> GamePublic:
    row = await game_crud.replace_game(db, game_id, payload)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return GamePublic.from_game(row)


@router.patch("/{game_id}", response_model=GamePublic)
async def patch_game(game_id: int, payload: GameUpdate, db: DbSession) -> GamePublic:
    row = await game_crud.update_game(db, game_id, payload)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
    return GamePublic.from_game(row)


@router.delete("/{game_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_game(game_id: int, db: DbSession) -> None:
    if not await game_crud.delete_game(db, game_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")
