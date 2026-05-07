"""Game storefront fields + game_comments

Revision ID: 20260207_0003
Revises: 20260207_0002
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260207_0003"
down_revision: Union[str, None] = "20260207_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("games", sa.Column("thumbnail_path", sa.String(length=300), nullable=True))
    op.add_column(
        "games",
        sa.Column("units_purchased", sa.Integer(), server_default="0", nullable=False),
    )
    op.add_column("games", sa.Column("tags_json", sa.Text(), nullable=True))
    op.add_column(
        "games",
        sa.Column("price_uah", sa.Integer(), server_default="0", nullable=False),
    )

    op.create_table(
        "game_comments",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("game_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_game_comments_game_id"), "game_comments", ["game_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_game_comments_game_id"), table_name="game_comments")
    op.drop_table("game_comments")
    op.drop_column("games", "price_uah")
    op.drop_column("games", "tags_json")
    op.drop_column("games", "units_purchased")
    op.drop_column("games", "thumbnail_path")
