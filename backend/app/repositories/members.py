import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.storage_member import StorageMember


class MemberRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, storage_id: uuid.UUID, user_id: uuid.UUID) -> StorageMember | None:
        stmt = select(StorageMember).where(
            StorageMember.storage_id == storage_id,
            StorageMember.user_id == user_id,
        )
        return self.db.scalars(stmt).first()

    def list_by_storage(self, storage_id: uuid.UUID) -> list[StorageMember]:
        stmt = (
            select(StorageMember)
            .where(StorageMember.storage_id == storage_id)
            .order_by(StorageMember.created_at)
        )
        return list(self.db.scalars(stmt).all())

    def add(
        self,
        storage_id: uuid.UUID,
        user_id: uuid.UUID,
        role: str,
        granted_by: uuid.UUID | None = None,
    ) -> StorageMember:
        member = StorageMember(
            storage_id=storage_id,
            user_id=user_id,
            role=role,
            granted_by=granted_by,
        )
        self.db.add(member)
        self.db.flush()
        return member

    def update_role(self, member: StorageMember, role: str) -> StorageMember:
        member.role = role
        self.db.flush()
        return member

    def remove(self, member: StorageMember) -> None:
        self.db.delete(member)
        self.db.flush()
