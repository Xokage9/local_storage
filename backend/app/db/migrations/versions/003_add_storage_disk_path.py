"""add disk_path to storages

Revision ID: 003
Revises: 002
Create Date: 2025-06-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

revision = "003"
down_revision = "002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("storages", sa.Column("disk_path", sa.String(500), nullable=True))


def downgrade() -> None:
    op.drop_column("storages", "disk_path")
