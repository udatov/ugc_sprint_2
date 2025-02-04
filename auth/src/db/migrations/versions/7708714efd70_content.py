"""content

Revision ID: 7708714efd70
Revises: 5de25e1fc010
Create Date: 2024-12-24 09:25:24.614932

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from core.content import DEFAULT_ROLES
from sqlalchemy.sql import column, table

revision: str = "7708714efd70"
down_revision: Union[str, None] = "5de25e1fc010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    role_table = table(
        "role",
        column("id", sa.UUID),
        column("name", sa.String),
        column("created_at", sa.DateTime),
    )
    op.bulk_insert(role_table, DEFAULT_ROLES)


def downgrade() -> None:
    op.execute(
        sa.text(
            "DELETE FROM role WHERE name IN ('anonymous', 'user', 'admin', 'subscriber')"
        )
    )
