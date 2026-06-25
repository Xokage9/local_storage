import uuid
from datetime import datetime

from pydantic import BaseModel


class FolderCreate(BaseModel):
    name: str
    parent_id: uuid.UUID | None = None


class FolderRename(BaseModel):
    name: str


class FolderRead(BaseModel):
    id: uuid.UUID
    storage_id: uuid.UUID
    parent_id: uuid.UUID | None = None
    name: str
    created_at: datetime

    model_config = {"from_attributes": True}
