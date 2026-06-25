import uuid
from datetime import datetime

from pydantic import BaseModel


class UserRead(BaseModel):
    id: uuid.UUID
    keycloak_id: str
    email: str
    display_name: str | None = None
    is_active: bool
    is_admin: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


class UserSearch(BaseModel):
    id: uuid.UUID
    email: str
    display_name: str | None = None

    model_config = {"from_attributes": True}
