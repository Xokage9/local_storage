import mimetypes
import os
import uuid
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.integrations.local_storage import CHUNK_SIZE, LocalFileStorage
from app.models.file import FileRecord
from app.models.storage import Storage
from app.repositories.files import FileRepository
from app.services.quota_service import QuotaService


class FileService:
    def __init__(
        self,
        repo: FileRepository,
        storage: LocalFileStorage,
        quota_service: QuotaService,
        db: Session | None = None,
    ) -> None:
        self.repo = repo
        self.storage = storage
        self.quota_service = quota_service
        self.db = db

    def disk_path_for(self, storage_id: uuid.UUID) -> str:
        if self.db:
            storage = self.db.get(Storage, storage_id)
            if storage and storage.disk_path:
                return storage.disk_path
        return str(storage_id)

    def list_files(
        self,
        storage_id: uuid.UUID,
        folder_id: uuid.UUID | None = None,
    ) -> list[FileRecord]:
        return self.repo.list_by_storage(storage_id, folder_id)

    def search_files(self, storage_id: uuid.UUID, query: str) -> list[FileRecord]:
        return self.repo.search(storage_id, query)

    async def upload_file(
        self,
        storage_id: uuid.UUID,
        folder_id: uuid.UUID | None,
        upload: UploadFile,
        uploaded_by: uuid.UUID,
    ) -> FileRecord:
        original_name = upload.filename or "unnamed"
        extension = os.path.splitext(original_name)[1]
        mime_type = upload.content_type or mimetypes.guess_type(original_name)[0]

        self.quota_service.check_upload_metadata(
            storage_id, filename=original_name, mime_type=mime_type
        )
        max_file_size, remaining = self.quota_service.get_size_limits(storage_id)

        file_id = uuid.uuid4()
        stored_filename, checksum, size = await self.storage.save_file_stream(
            self.disk_path_for(storage_id),
            file_id,
            self._iter_upload_with_limits(upload, max_file_size, remaining),
            extension,
        )

        return self.repo.create(
            id=file_id,
            storage_id=storage_id,
            folder_id=folder_id,
            original_name=original_name,
            stored_filename=stored_filename,
            mime_type=mime_type,
            size_bytes=size,
            checksum_sha256=checksum,
            uploaded_by=uploaded_by,
        )

    @staticmethod
    async def _iter_upload_with_limits(
        upload: UploadFile,
        max_file_size: int | None,
        remaining: int | None,
    ) -> AsyncIterator[bytes]:
        size = 0
        while True:
            chunk = await upload.read(CHUNK_SIZE)
            if not chunk:
                break
            size += len(chunk)
            if max_file_size is not None and size > max_file_size:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=f"File size exceeds maximum {max_file_size}",
                )
            if remaining is not None and size > remaining:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail="Storage quota exceeded",
                )
            yield chunk

    def get_file(self, file_id: uuid.UUID) -> FileRecord:
        record = self.repo.get_by_id(file_id)
        if record is None or record.is_deleted:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        return record

    def download_file(self, file_id: uuid.UUID) -> tuple[bytes, str, str | None]:
        record = self.get_file(file_id)
        disk_path = self.disk_path_for(record.storage_id)
        data = self.storage.read_file(disk_path, record.stored_filename)
        return data, record.original_name, record.mime_type

    def stream_file(
        self, file_id: uuid.UUID
    ) -> tuple[Iterator[bytes], str, str | None, int]:
        record = self.get_file(file_id)
        disk_path = self.disk_path_for(record.storage_id)
        chunks = self.storage.iter_file(disk_path, record.stored_filename)
        return chunks, record.original_name, record.mime_type, record.size_bytes

    def rename_file(self, file_id: uuid.UUID, new_name: str) -> FileRecord:
        record = self.get_file(file_id)
        return self.repo.rename(record, new_name)

    def move_file(self, file_id: uuid.UUID, folder_id: uuid.UUID | None) -> FileRecord:
        record = self.get_file(file_id)
        return self.repo.move(record, folder_id)

    def delete_file(self, file_id: uuid.UUID) -> None:
        record = self.get_file(file_id)
        self.repo.soft_delete(record)

    def get_file_path(self, file_id: uuid.UUID) -> Path:
        record = self.get_file(file_id)
        disk_path = self.disk_path_for(record.storage_id)
        return self.storage.get_file_path(disk_path, record.stored_filename)
