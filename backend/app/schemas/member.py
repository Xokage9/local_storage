import uuid
from datetime import datetime

from pydantic import BaseModel


class MemberCreate(BaseModel):
    user_id: uuid.UUID
    role: str = "viewer"


class MemberUpdate(BaseModel):
    role: str


class MemberRead(BaseModel):
    id: uuid.UUID
    storage_id: uuid.UUID
    user_id: uuid.UUID
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}
