import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.storage_policy import StoragePolicy
from app.repositories.files import FileRepository


class QuotaService:
    def __init__(self, db: Session, file_repo: FileRepository) -> None:
        self.db = db
        self.file_repo = file_repo

    def get_policy(self, storage_id: uuid.UUID) -> StoragePolicy | None:
        return self.db.get(StoragePolicy, storage_id) or self.db.query(StoragePolicy).filter(
            StoragePolicy.storage_id == storage_id
        ).first()

    def check_upload_metadata(
        self,
        storage_id: uuid.UUID,
        filename: str | None = None,
        mime_type: str | None = None,
    ) -> None:
        """Проверки, которые можно сделать до записи (расширение и MIME-тип)."""
        policy = self.db.query(StoragePolicy).filter(
            StoragePolicy.storage_id == storage_id
        ).first()
        if not policy:
            return

        if policy.allowed_extensions and filename:
            import os
            ext = os.path.splitext(filename)[1].lower()
            allowed = [e.lower() if e.startswith(".") else f".{e.lower()}" for e in policy.allowed_extensions]
            if ext not in allowed:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File extension '{ext}' is not allowed. Allowed: {', '.join(allowed)}",
                )

        if policy.allowed_mime_types and mime_type:
            if mime_type not in policy.allowed_mime_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"MIME type '{mime_type}' is not allowed. Allowed: {', '.join(policy.allowed_mime_types)}",
                )

    def get_size_limits(
        self, storage_id: uuid.UUID
    ) -> tuple[int | None, int | None]:
        """Возвращает (макс. размер файла, доступный остаток квоты) для стрима.

        None означает «без ограничений» (политика для хранилища не задана).
        """
        policy = self.db.query(StoragePolicy).filter(
            StoragePolicy.storage_id == storage_id
        ).first()
        if not policy:
            return None, None
        current_usage = self.file_repo.get_storage_usage(storage_id)
        remaining = policy.max_storage_bytes - current_usage
        return policy.max_file_size_bytes, remaining

    def get_usage(self, storage_id: uuid.UUID) -> dict:
        policy = self.db.query(StoragePolicy).filter(
            StoragePolicy.storage_id == storage_id
        ).first()
        current_usage = self.file_repo.get_storage_usage(storage_id)
        total_files = self.file_repo.count_by_storage(storage_id)

        quota = policy.max_storage_bytes if policy else 0
        return {
            "total_files": total_files,
            "total_size_bytes": current_usage,
            "quota_bytes": quota,
            "usage_percent": round((current_usage / quota * 100), 2) if quota else 0,
        }
