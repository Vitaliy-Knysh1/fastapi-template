from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.cart_item import CartItem


async def list_cart_items(db: AsyncSession, user_id: int) -> list[CartItem]:
    result = await db.execute(
        select(CartItem)
        .where(CartItem.user_id == user_id)
        .options(selectinload(CartItem.game))
        .order_by(CartItem.id),
    )
    return list(result.scalars().all())


async def cart_item_count(db: AsyncSession, user_id: int) -> int:
    items = await list_cart_items(db, user_id)
    return sum(i.quantity for i in items)


async def get_cart_row(db: AsyncSession, user_id: int, game_id: int) -> CartItem | None:
    result = await db.execute(
        select(CartItem).where(CartItem.user_id == user_id, CartItem.game_id == game_id),
    )
    return result.scalar_one_or_none()


async def add_item(db: AsyncSession, user_id: int, game_id: int, quantity: int = 1) -> CartItem:
    row = await get_cart_row(db, user_id, game_id)
    if row is None:
        row = CartItem(user_id=user_id, game_id=game_id, quantity=max(1, quantity))
        db.add(row)
    else:
        row.quantity += quantity
        if row.quantity < 1:
            row.quantity = 1
    await db.flush()
    await db.refresh(row)
    return row


async def set_quantity(db: AsyncSession, user_id: int, game_id: int, quantity: int) -> CartItem | None:
    row = await get_cart_row(db, user_id, game_id)
    if row is None:
        return None
    if quantity <= 0:
        await db.delete(row)
        await db.flush()
        return None
    row.quantity = quantity
    await db.flush()
    await db.refresh(row)
    return row


async def remove_item(db: AsyncSession, user_id: int, game_id: int) -> bool:
    row = await get_cart_row(db, user_id, game_id)
    if row is None:
        return False
    await db.delete(row)
    await db.flush()
    return True


async def clear_cart(db: AsyncSession, user_id: int) -> None:
    await db.execute(delete(CartItem).where(CartItem.user_id == user_id))
    await db.flush()
