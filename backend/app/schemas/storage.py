import uuid
from datetime import datetime

from pydantic import BaseModel


class StorageCreate(BaseModel):
    name: str
    storage_type: str = "global"


class StorageUpdate(BaseModel):
    name: str | None = None


class StorageRead(BaseModel):
    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    storage_type: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class StoragePolicyRead(BaseModel):
    max_file_size_bytes: int
    max_storage_bytes: int
    allowed_extensions: list[str] | None = None
    allowed_mime_types: list[str] | None = None

    model_config = {"from_attributes": True}


class StoragePolicyUpdate(BaseModel):
    max_file_size_bytes: int | None = None
    max_storage_bytes: int | None = None
    allowed_extensions: list[str] | None = None
    allowed_mime_types: list[str] | None = None


class StorageStats(BaseModel):
    total_files: int
    total_size_bytes: int
    quota_bytes: int
    usage_percent: float
