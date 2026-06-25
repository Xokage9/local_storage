import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.storage import Storage
from app.models.storage_member import StorageMember
from app.models.storage_policy import StoragePolicy


class StorageRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, storage_id: uuid.UUID) -> Storage | None:
        return self.db.get(Storage, storage_id)

    def list_by_owner(self, owner_id: uuid.UUID) -> list[Storage]:
        stmt = (
            select(Storage)
            .where(Storage.owner_id == owner_id, Storage.is_active.is_(True))
            .order_by(Storage.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_global(self) -> list[Storage]:
        stmt = (
            select(Storage)
            .where(Storage.storage_type == "global", Storage.is_active.is_(True))
            .order_by(Storage.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def list_shared_with_user(self, user_id: uuid.UUID) -> list[Storage]:
        stmt = (
            select(Storage)
            .join(StorageMember, StorageMember.storage_id == Storage.id)
            .where(
                StorageMember.user_id == user_id,
                Storage.owner_id != user_id,
                Storage.is_active.is_(True),
            )
            .order_by(Storage.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def create(
        self,
        name: str,
        owner_id: uuid.UUID,
        storage_type: str,
        disk_path: str | None = None,
    ) -> Storage:
        storage = Storage(name=name, owner_id=owner_id, storage_type=storage_type, disk_path=disk_path)
        self.db.add(storage)
        self.db.flush()

        member = StorageMember(
            storage_id=storage.id, user_id=owner_id, role="owner"
        )
        self.db.add(member)

        policy = StoragePolicy(storage_id=storage.id)
        self.db.add(policy)

        self.db.flush()
        return storage

    def update(self, storage: Storage, **kwargs) -> Storage:
        for key, value in kwargs.items():
            if hasattr(storage, key) and value is not None:
                setattr(storage, key, value)
        self.db.flush()
        return storage

    def soft_delete(self, storage: Storage) -> None:
        storage.is_active = False
        self.db.flush()

    def list_all(self, offset: int = 0, limit: int = 50) -> list[Storage]:
        stmt = select(Storage).offset(offset).limit(limit).order_by(Storage.created_at.desc())
        return list(self.db.scalars(stmt).all())
