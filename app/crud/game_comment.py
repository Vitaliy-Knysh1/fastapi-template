from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.game_comment import GameComment
from app.models.user import User


async def list_for_game_with_authors(
    db: AsyncSession,
    game_id: int,
) -> list[tuple[GameComment, str]]:
    result = await db.execute(
        select(GameComment, User.name)
        .join(User, GameComment.user_id == User.id)
        .where(GameComment.game_id == game_id)
        .order_by(GameComment.created_at.desc()),
    )
    return list(result.all())


async def create_comment(db: AsyncSession, *, game_id: int, user_id: int, body: str) -> GameComment:
    row = GameComment(game_id=game_id, user_id=user_id, body=body.strip())
    db.add(row)
    await db.flush()
    await db.refresh(row)
    return row
