"""Cart, billing snapshot, per-game luck stats

Revision ID: 20260207_0004
Revises: 20260207_0003
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260207_0004"
down_revision: Union[str, None] = "20260207_0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), server_default="1", nullable=False),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "game_id", name="uq_cart_user_game"),
    )
    op.create_index(op.f("ix_cart_items_user_id"), "cart_items", ["user_id"], unique=False)

    op.add_column(
        "games",
        sa.Column("luck_wins_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column(
        "games",
        sa.Column("luck_losses_count", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column("orders", sa.Column("billing_snapshot_json", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("orders", "billing_snapshot_json")
    op.drop_column("games", "luck_losses_count")
    op.drop_column("games", "luck_wins_count")
    op.drop_index(op.f("ix_cart_items_user_id"), table_name="cart_items")
    op.drop_table("cart_items")
