import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.file_access import FileAccess


class FileAccessRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, file_id: uuid.UUID, user_id: uuid.UUID) -> FileAccess | None:
        stmt = select(FileAccess).where(
            FileAccess.file_id == file_id,
            FileAccess.user_id == user_id,
        )
        return self.db.scalars(stmt).first()

    def list_by_file(self, file_id: uuid.UUID) -> list[FileAccess]:
        stmt = (
            select(FileAccess)
            .where(FileAccess.file_id == file_id)
            .order_by(FileAccess.created_at)
        )
        return list(self.db.scalars(stmt).all())

    def list_by_user(self, user_id: uuid.UUID) -> list[FileAccess]:
        stmt = (
            select(FileAccess)
            .where(FileAccess.user_id == user_id)
            .order_by(FileAccess.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def grant(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID,
        permission: str,
        granted_by: uuid.UUID,
    ) -> FileAccess:
        access = FileAccess(
            file_id=file_id,
            user_id=user_id,
            permission=permission,
            granted_by=granted_by,
        )
        self.db.add(access)
        self.db.flush()
        return access

    def revoke(self, access: FileAccess) -> None:
        self.db.delete(access)
        self.db.flush()
