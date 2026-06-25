import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent


class AuditRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        action: str,
        user_id: uuid.UUID | None = None,
        storage_id: uuid.UUID | None = None,
        file_id: uuid.UUID | None = None,
        details: dict | None = None,
        ip_address: str | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            user_id=user_id,
            storage_id=storage_id,
            file_id=file_id,
            action=action,
            details=details,
            ip_address=ip_address,
        )
        self.db.add(event)
        self.db.flush()
        return event

    def list_events(
        self,
        storage_id: uuid.UUID | None = None,
        user_id: uuid.UUID | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> list[AuditEvent]:
        stmt = select(AuditEvent)
        if storage_id:
            stmt = stmt.where(AuditEvent.storage_id == storage_id)
        if user_id:
            stmt = stmt.where(AuditEvent.user_id == user_id)
        stmt = stmt.order_by(AuditEvent.created_at.desc()).offset(offset).limit(limit)
        return list(self.db.scalars(stmt).all())
