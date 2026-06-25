import uuid
from datetime import datetime

from pydantic import BaseModel


class FileRead(BaseModel):
    id: uuid.UUID
    storage_id: uuid.UUID
    folder_id: uuid.UUID | None = None
    original_name: str
    mime_type: str | None = None
    size_bytes: int
    is_deleted: bool
    uploaded_by: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class FileRename(BaseModel):
    name: str


class FileMove(BaseModel):
    folder_id: uuid.UUID | None = None


class FileAccessCreate(BaseModel):
    user_id: uuid.UUID
    permission: str = "download"


class FileAccessRead(BaseModel):
    id: uuid.UUID
    file_id: uuid.UUID
    user_id: uuid.UUID
    permission: str
    granted_by: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class FileSearchResult(BaseModel):
    id: uuid.UUID
    original_name: str
    mime_type: str | None = None
    size_bytes: int
    folder_id: uuid.UUID | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
