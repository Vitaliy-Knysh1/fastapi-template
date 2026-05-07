"""Add users.password_hash for auth

Revision ID: 20260207_0002
Revises: 20260207_0001
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "20260207_0002"
down_revision: Union[str, None] = "20260207_0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "password_hash")
