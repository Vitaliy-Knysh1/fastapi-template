from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.order import Order
from app.models.order_line import OrderLine
from app.schemas.order import OrderCreate, OrderUpdate


async def refresh_order_total(db: AsyncSession, order_id: int) -> None:
    result = await db.execute(select(OrderLine).where(OrderLine.order_id == order_id))
    lines = list(result.scalars().all())
    total = sum(line.quantity * line.unit_price_cents + line.wheel_adjustment_cents for line in lines)
    order = await db.get(Order, order_id)
    if order is None:
        return
    order.total_cents = int(total)
    await db.flush()


async def create_order(db: AsyncSession, payload: OrderCreate) -> Order:
    order = Order(user_id=payload.user_id, status=payload.status, total_cents=0)
    db.add(order)
    await db.flush()
    await db.refresh(order)
    return order


async def get_order(db: AsyncSession, order_id: int) -> Order | None:
    result = await db.execute(
        select(Order)
        .where(Order.id == order_id)
        .options(
            selectinload(Order.lines),
            selectinload(Order.user),
        ),
    )
    return result.scalar_one_or_none()


async def list_orders(db: AsyncSession, skip: int = 0, limit: int = 100) -> list[Order]:
    result = await db.execute(
        select(Order)
        .offset(skip)
        .limit(limit)
        .order_by(Order.id)
        .options(selectinload(Order.lines)),
    )
    return list(result.scalars().unique().all())


async def update_order(db: AsyncSession, order_id: int, payload: OrderUpdate) -> Order | None:
    order = await db.get(Order, order_id)
    if order is None:
        return None
    data = payload.model_dump(exclude_unset=True)
    for key, val in data.items():
        setattr(order, key, val)
    await db.flush()
    await db.refresh(order)
    return order


async def delete_order(db: AsyncSession, order_id: int) -> bool:
    order = await db.get(Order, order_id)
    if order is None:
        return False
    db.delete(order)
    await db.flush()
    return True
