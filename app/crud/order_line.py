from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import order as order_crud
from app.models.order_line import OrderLine
from app.schemas.order_line import OrderLineCreate, OrderLineUpdate


async def create_order_line(db: AsyncSession, payload: OrderLineCreate) -> OrderLine:
    row = OrderLine(**payload.model_dump())
    db.add(row)
    await db.flush()
    await db.refresh(row)
    await order_crud.refresh_order_total(db, payload.order_id)
    return row


async def get_order_line(db: AsyncSession, line_id: int) -> OrderLine | None:
    return await db.get(OrderLine, line_id)


async def list_order_lines(db: AsyncSession, skip: int = 0, limit: int = 200) -> list[OrderLine]:
    result = await db.execute(select(OrderLine).offset(skip).limit(limit).order_by(OrderLine.id))
    return list(result.scalars().all())


async def lines_for_order(db: AsyncSession, order_id: int) -> list[OrderLine]:
    result = await db.execute(select(OrderLine).where(OrderLine.order_id == order_id))
    return list(result.scalars().all())


async def replace_order_line(
    db: AsyncSession,
    line_id: int,
    payload: OrderLineCreate,
) -> OrderLine | None:
    row = await get_order_line(db, line_id)
    if row is None:
        return None
    old_order_id = row.order_id
    data = payload.model_dump()
    row.order_id = data["order_id"]
    row.game_id = data["game_id"]
    row.quantity = data["quantity"]
    row.unit_price_cents = data["unit_price_cents"]
    row.wheel_adjustment_cents = data["wheel_adjustment_cents"]
    await db.flush()
    await db.refresh(row)
    await order_crud.refresh_order_total(db, old_order_id)
    await order_crud.refresh_order_total(db, row.order_id)
    return row


async def update_order_line(db: AsyncSession, line_id: int, payload: OrderLineUpdate) -> OrderLine | None:
    row = await get_order_line(db, line_id)
    if row is None:
        return None
    order_id = row.order_id
    for key, val in payload.model_dump(exclude_unset=True).items():
        setattr(row, key, val)
    await db.flush()
    await db.refresh(row)
    await order_crud.refresh_order_total(db, order_id)
    return row


async def delete_order_line(db: AsyncSession, line_id: int) -> bool:
    row = await get_order_line(db, line_id)
    if row is None:
        return False
    order_id = row.order_id
    db.delete(row)
    await db.flush()
    await order_crud.refresh_order_total(db, order_id)
    return True
