"""add is_admin to users

Revision ID: 002
Revises: 001
Create Date: 2025-06-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("is_admin", sa.Boolean(), server_default="false"))


def downgrade() -> None:
    op.drop_column("users", "is_admin")
