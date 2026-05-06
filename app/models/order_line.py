from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.game import Game
    from app.models.order import Order


class OrderLine(Base):
    """
    Line item for a purchase.
    wheel_adjustment_cents: +1 or -1 from the promotional wheel (placeholder for game store twist).
    """

    __tablename__ = "order_lines"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id", ondelete="RESTRICT"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    unit_price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    wheel_adjustment_cents: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    order: Mapped[Order] = relationship(back_populates="lines")
    game: Mapped[Game] = relationship(back_populates="order_lines")
