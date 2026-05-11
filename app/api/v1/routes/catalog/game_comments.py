from fastapi import APIRouter, HTTPException, status

from app.api.deps import CurrentUser, DbSession
from app.crud import game as game_crud
from app.crud import game_comment as comment_crud
from app.schemas.game_comment import GameCommentCreate, GameCommentPublic

router = APIRouter()


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
