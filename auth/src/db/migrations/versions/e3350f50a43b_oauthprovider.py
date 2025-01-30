"""oauthprovider

Revision ID: e3350f50a43b
Revises: 7708714efd70
Create Date: 2025-01-15 19:58:49.397651

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from core.content import DEFAULT_OAUTHPROVIDERS
from sqlalchemy.sql import column, table

revision: str = "e3350f50a43b"
down_revision: Union[str, None] = "7708714efd70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "oauthprovider",
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_oauthprovider_name"), "oauthprovider", ["name"], unique=True
    )
    op.create_table(
        "useroauthprovider",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=50), nullable=True),
        sa.Column("last_name", sa.String(length=50), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("oauthprovider_id", sa.UUID(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["oauthprovider_id"], ["oauthprovider.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    oauthprovider_table = table(
        "oauthprovider",
        column("id", sa.UUID),
        column("name", sa.String),
        column("created_at", sa.DateTime),
    )
    op.bulk_insert(oauthprovider_table, DEFAULT_OAUTHPROVIDERS)


def downgrade() -> None:
    op.drop_table("oauthprovider")
    op.drop_table("useroauthprovider")
    op.drop_index(op.f("ix_oauthprovider_name"), table_name="oauthprovider")
