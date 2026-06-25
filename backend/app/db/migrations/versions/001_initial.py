"""initial schema

Revision ID: 001
Revises:
Create Date: 2025-01-01 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("keycloak_id", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("keycloak_id"),
        sa.UniqueConstraint("email"),
    )

    op.create_table(
        "storages",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("owner_id", sa.Uuid(), nullable=False),
        sa.Column("storage_type", sa.String(20), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "storage_policies",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("storage_id", sa.Uuid(), nullable=False),
        sa.Column("max_file_size_bytes", sa.BigInteger(), server_default="104857600"),
        sa.Column("max_storage_bytes", sa.BigInteger(), server_default="1073741824"),
        sa.Column("allowed_extensions", sa.JSON(), nullable=True),
        sa.Column("allowed_mime_types", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["storage_id"], ["storages.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_id"),
    )

    op.create_table(
        "storage_members",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("storage_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("granted_by", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["storage_id"], ["storages.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["granted_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_id", "user_id", name="uq_storage_user"),
    )

    op.create_table(
        "folders",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("storage_id", sa.Uuid(), nullable=False),
        sa.Column("parent_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.ForeignKeyConstraint(["storage_id"], ["storages.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["folders.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "files",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("storage_id", sa.Uuid(), nullable=False),
        sa.Column("folder_id", sa.Uuid(), nullable=True),
        sa.Column("original_name", sa.String(500), nullable=False),
        sa.Column("stored_filename", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(255), nullable=True),
        sa.Column("size_bytes", sa.BigInteger(), nullable=False, server_default="0"),
        sa.Column("checksum_sha256", sa.String(64), nullable=True),
        sa.Column("is_deleted", sa.Boolean(), server_default="false"),
        sa.Column("uploaded_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["storage_id"], ["storages.id"]),
        sa.ForeignKeyConstraint(["folder_id"], ["folders.id"]),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "file_access",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("permission", sa.String(20), nullable=False),
        sa.Column("granted_by", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["granted_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_id", "user_id", name="uq_file_user_access"),
    )

    op.create_table(
        "share_links",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("token", sa.String(255), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("created_by", sa.Uuid(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("max_downloads", sa.Integer(), nullable=True),
        sa.Column("download_count", sa.Integer(), server_default="0"),
        sa.Column("is_revoked", sa.Boolean(), server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_share_links_token", "share_links", ["token"], unique=True)

    op.create_table(
        "audit_events",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=True),
        sa.Column("storage_id", sa.Uuid(), nullable=True),
        sa.Column("file_id", sa.Uuid(), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["storage_id"], ["storages.id"]),
        sa.ForeignKeyConstraint(["file_id"], ["files.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("audit_events")
    op.drop_index("ix_share_links_token", "share_links")
    op.drop_table("share_links")
    op.drop_table("file_access")
    op.drop_table("files")
    op.drop_table("folders")
    op.drop_table("storage_members")
    op.drop_table("storage_policies")
    op.drop_table("storages")
    op.drop_table("users")
