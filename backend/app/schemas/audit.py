import uuid
from datetime import datetime

from pydantic import BaseModel


class AuditEventRead(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID | None = None
    storage_id: uuid.UUID | None = None
    file_id: uuid.UUID | None = None
    action: str
    details: dict | None = None
    ip_address: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}
