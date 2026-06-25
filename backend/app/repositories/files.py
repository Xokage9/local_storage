import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.file import FileRecord


class FileRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, file_id: uuid.UUID) -> FileRecord | None:
        return self.db.get(FileRecord, file_id)

    def list_by_storage(
        self,
        storage_id: uuid.UUID,
        folder_id: uuid.UUID | None = None,
        include_deleted: bool = False,
    ) -> list[FileRecord]:
        stmt = select(FileRecord).where(
            FileRecord.storage_id == storage_id,
            FileRecord.folder_id == folder_id,
        )
        if not include_deleted:
            stmt = stmt.where(FileRecord.is_deleted.is_(False))
        stmt = stmt.order_by(FileRecord.original_name)
        return list(self.db.scalars(stmt).all())

    def search(self, storage_id: uuid.UUID, query: str) -> list[FileRecord]:
        stmt = (
            select(FileRecord)
            .where(
                FileRecord.storage_id == storage_id,
                FileRecord.is_deleted.is_(False),
                FileRecord.original_name.ilike(f"%{query}%"),
            )
            .order_by(FileRecord.original_name)
            .limit(50)
        )
        return list(self.db.scalars(stmt).all())

    def create(self, **kwargs) -> FileRecord:
        record = FileRecord(**kwargs)
        self.db.add(record)
        self.db.flush()
        return record

    def rename(self, record: FileRecord, new_name: str) -> FileRecord:
        record.original_name = new_name
        self.db.flush()
        return record

    def move(self, record: FileRecord, folder_id: uuid.UUID | None) -> FileRecord:
        record.folder_id = folder_id
        self.db.flush()
        return record

    def soft_delete(self, record: FileRecord) -> None:
        record.is_deleted = True
        record.deleted_at = func.now()
        self.db.flush()

    def get_storage_usage(self, storage_id: uuid.UUID) -> int:
        stmt = select(func.coalesce(func.sum(FileRecord.size_bytes), 0)).where(
            FileRecord.storage_id == storage_id,
            FileRecord.is_deleted.is_(False),
        )
        return self.db.scalar(stmt) or 0

    def count_by_storage(self, storage_id: uuid.UUID) -> int:
        stmt = select(func.count(FileRecord.id)).where(
            FileRecord.storage_id == storage_id,
            FileRecord.is_deleted.is_(False),
        )
        return self.db.scalar(stmt) or 0
