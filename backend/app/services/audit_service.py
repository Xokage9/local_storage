import uuid

from app.models.audit_event import AuditEvent
from app.repositories.audit import AuditRepository


class AuditService:
    def __init__(self, repo: AuditRepository) -> None:
        self.repo = repo

    def log(
        self,
        action: str,
        user_id: uuid.UUID | None = None,
        storage_id: uuid.UUID | None = None,
        file_id: uuid.UUID | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditEvent:
        return self.repo.create(
            action=action,
            user_id=user_id,
            storage_id=storage_id,
            file_id=file_id,
            details=details,
            ip_address=ip_address,
        )

    def list_events(
        self,
        storage_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[AuditEvent]:
        return self.repo.list_events(storage_id, user_id, offset, limit)
