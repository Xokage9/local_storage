import uuid
from datetime import datetime

from pydantic import BaseModel


class ShareLinkCreate(BaseModel):
    expires_in_hours: int | None = 24
    max_downloads: int | None = None


class ShareLinkRead(BaseModel):
    id: uuid.UUID
    token: str
    file_id: uuid.UUID
    created_by: uuid.UUID
    expires_at: datetime | None = None
    max_downloads: int | None = None
    download_count: int
    is_revoked: bool
    created_at: datetime

    model_config = {"from_attributes": True}
