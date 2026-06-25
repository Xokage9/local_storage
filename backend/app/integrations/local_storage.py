import hashlib
import shutil
import uuid
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

from app.config import settings

CHUNK_SIZE = 1024 * 1024


class LocalFileStorage:

    def __init__(self, base_path: str | None = None) -> None:
        self.base_path = Path(base_path or settings.file_storage_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def ensure_dir(self, disk_path: str) -> Path:
        folder = self.base_path / disk_path
        folder.mkdir(parents=True, exist_ok=True)
        return folder

    def save_file(
        self, disk_path: str, file_id: uuid.UUID, data: bytes, extension: str = ""
    ) -> tuple[str, str]:
        filename = f"{file_id}{extension}"
        (self.ensure_dir(disk_path) / filename).write_bytes(data)
        checksum = hashlib.sha256(data).hexdigest()
        return filename, checksum

    async def save_file_stream(
        self,
        disk_path: str,
        file_id: uuid.UUID,
        chunks: AsyncIterator[bytes],
        extension: str = "",
    ) -> tuple[str, str, int]:
        filename = f"{file_id}{extension}"
        file_path = self.ensure_dir(disk_path) / filename
        hasher = hashlib.sha256()
        size = 0
        try:
            with file_path.open("wb") as f:
                async for chunk in chunks:
                    f.write(chunk)
                    hasher.update(chunk)
                    size += len(chunk)
        except BaseException:
            file_path.unlink(missing_ok=True)
            raise
        return filename, hasher.hexdigest(), size

    def read_file(self, disk_path: str, stored_filename: str) -> bytes:
        file_path = self.ensure_dir(disk_path) / stored_filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {stored_filename}")
        return file_path.read_bytes()

    def iter_file(
        self, disk_path: str, stored_filename: str, chunk_size: int = CHUNK_SIZE
    ) -> Iterator[bytes]:
        file_path = self.ensure_dir(disk_path) / stored_filename
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {stored_filename}")
        with file_path.open("rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

    def delete_file(self, disk_path: str, stored_filename: str) -> bool:
        file_path = self.ensure_dir(disk_path) / stored_filename
        if not file_path.exists():
            return False
        file_path.unlink()
        return True

    def delete_storage_dir(self, disk_path: str) -> None:
        folder = self.base_path / disk_path
        if folder.exists():
            shutil.rmtree(folder)

    def get_file_path(self, disk_path: str, stored_filename: str) -> Path:
        return self.ensure_dir(disk_path) / stored_filename

    def file_exists(self, disk_path: str, stored_filename: str) -> bool:
        return (self.ensure_dir(disk_path) / stored_filename).exists()


local_storage = LocalFileStorage()
