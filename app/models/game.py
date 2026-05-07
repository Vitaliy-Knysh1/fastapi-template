from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.cart_item import CartItem
    from app.models.game_comment import GameComment
    from app.models.genre import Genre
    from app.models.order_line import OrderLine


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    genre_id: Mapped[int] = mapped_column(ForeignKey("genres.id", ondelete="RESTRICT"), nullable=False)
    title: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    slug: Mapped[str] = mapped_column(String(220), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_cents: Mapped[int] = mapped_column(Integer, nullable=False)
    stock: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    thumbnail_path: Mapped[str | None] = mapped_column(String(300), nullable=True)
    units_purchased: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    tags_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    price_uah: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    luck_wins_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")
    luck_losses_count: Mapped[int] = mapped_column(Integer, nullable=False, server_default="0")

    genre: Mapped[Genre] = relationship(back_populates="games")
    order_lines: Mapped[list[OrderLine]] = relationship(back_populates="game")
    comments: Mapped[list["GameComment"]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan",
    )
    cart_items: Mapped[list["CartItem"]] = relationship(back_populates="game")
