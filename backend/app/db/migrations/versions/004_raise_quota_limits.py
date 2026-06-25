"""raise default quota limits (file -> 1GB, storage -> 3GB)

Revision ID: 004
Revises: 003
Create Date: 2026-06-23 00:00:00.000000
"""

from alembic import op

revision = "004"
down_revision = "003"
branch_labels = None
depends_on = None

# Старые дефолты, заданные при создании политик ранее.
OLD_FILE_LIMIT = 104_857_600       # 100 МБ
OLD_STORAGE_LIMIT = 1_073_741_824  # 1 ГБ

# Новые лимиты.
NEW_FILE_LIMIT = 1_073_741_824     # 1 ГБ
NEW_STORAGE_LIMIT = 3_221_225_472  # 3 ГБ


def upgrade() -> None:
    # Поднимаем только политики со старыми дефолтными значениями,
    # чтобы не затирать лимиты, которые админ настроил вручную.
    op.execute(
        f"UPDATE storage_policies SET max_file_size_bytes = {NEW_FILE_LIMIT} "
        f"WHERE max_file_size_bytes = {OLD_FILE_LIMIT}"
    )
    op.execute(
        f"UPDATE storage_policies SET max_storage_bytes = {NEW_STORAGE_LIMIT} "
        f"WHERE max_storage_bytes = {OLD_STORAGE_LIMIT}"
    )


def downgrade() -> None:
    op.execute(
        f"UPDATE storage_policies SET max_file_size_bytes = {OLD_FILE_LIMIT} "
        f"WHERE max_file_size_bytes = {NEW_FILE_LIMIT}"
    )
    op.execute(
        f"UPDATE storage_policies SET max_storage_bytes = {OLD_STORAGE_LIMIT} "
        f"WHERE max_storage_bytes = {NEW_STORAGE_LIMIT}"
    )
