from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from app.models.cart_item import CartItem


class CartItemAdd(BaseModel):
    game_id: int = Field(..., gt=0)
    quantity: int = Field(default=1, ge=1, le=99)


class CartItemQuantity(BaseModel):
    quantity: int = Field(..., ge=1, le=99)


class CartLinePublic(BaseModel):
    game_id: int
    slug: str
    title: str
    quantity: int
    unit_price_uah: int
    line_subtotal_uah: int


class CartPublic(BaseModel):
    items: list[CartLinePublic]
    item_count: int
    subtotal_uah: int


def cart_rows_to_public(rows: list["CartItem"]) -> CartPublic:
    items: list[CartLinePublic] = []
    for row in rows:
        g = row.game
        uah = g.price_uah
        items.append(
            CartLinePublic(
                game_id=g.id,
                slug=g.slug,
                title=g.title,
                quantity=row.quantity,
                unit_price_uah=uah,
                line_subtotal_uah=uah * row.quantity,
            ),
        )
    item_count = sum(r.quantity for r in rows)
    subtotal_uah = sum(i.line_subtotal_uah for i in items)
    return CartPublic(items=items, item_count=item_count, subtotal_uah=subtotal_uah)
