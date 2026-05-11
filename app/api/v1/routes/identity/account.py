from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import CurrentUser, DbSession
from app.models.order import Order
from app.schemas.account import AccountStats, AccountSummary

router = APIRouter()


@router.get("/summary", response_model=AccountSummary)
async def account_summary(user: CurrentUser) -> AccountSummary:
    return AccountSummary.model_validate(user)


@router.get("/stats", response_model=AccountStats)
async def account_stats(user: CurrentUser, db: DbSession) -> AccountStats:
    result = await db.execute(select(func.count(Order.id)).where(Order.user_id == user.id))
    count = int(result.scalar_one() or 0)
    return AccountStats(orders_count=count)
