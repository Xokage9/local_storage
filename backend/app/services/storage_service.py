import re
import uuid

from fastapi import HTTPException, status

from app.models.storage import Storage
from app.repositories.members import MemberRepository
from app.repositories.storages import StorageRepository


def slugify(name: str) -> str:
    "ренейп параши всякой в нормальный вид для папок на диске"
    cleaned = re.sub(r"[^\w\s-]", "", name.lower().strip())
    cleaned = re.sub(r"\s+", "_", cleaned)
    return cleaned or "storage"


class StorageService:
    def __init__(self, repo: StorageRepository, member_repo: MemberRepository) -> None:
        self.repo = repo
        self.member_repo = member_repo

    def create_personal_storage(self, owner_id: uuid.UUID, username: str) -> Storage:
        return self.repo.create(
            name="Личное хранилище",
            owner_id=owner_id,
            storage_type="personal",
            disk_path=f"{slugify(username)}_local",
        )

    def create_storage(
        self, name: str, owner_id: uuid.UUID, storage_type: str = "global", username: str = ""
    ) -> Storage:
        if storage_type == "personal":
            disk_path = f"{slugify(username)}_local"
        else:
            disk_path = f"{slugify(username)}_global_{slugify(name)}"
        return self.repo.create(
            name=name, owner_id=owner_id, storage_type=storage_type, disk_path=disk_path
        )

    def get_storage(self, storage_id: uuid.UUID) -> Storage:
        storage = self.repo.get_by_id(storage_id)
        if not storage or not storage.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Storage not found")
        return storage

    def list_user_storages(self, user_id: uuid.UUID) -> dict:
        return {
            "own": self.repo.list_by_owner(user_id),
            "shared": self.repo.list_shared_with_user(user_id),
            "global": self.repo.list_global(),
        }

    def get_user_role(self, storage_id: uuid.UUID, user_id: uuid.UUID) -> str | None:
        member = self.member_repo.get(storage_id, user_id)
        return member.role if member else None

    def require_role(
        self, storage_id: uuid.UUID, user_id: uuid.UUID, roles: tuple[str, ...]
    ) -> None:
        if self.get_user_role(storage_id, user_id) not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )

    def update_storage(
        self, storage_id: uuid.UUID, user_id: uuid.UUID, **kwargs
    ) -> Storage:
        storage = self.get_storage(storage_id)
        self.require_role(storage_id, user_id, ("owner", "admin"))
        return self.repo.update(storage, **kwargs)

    def delete_storage(self, storage_id: uuid.UUID, user_id: uuid.UUID) -> None:
        storage = self.get_storage(storage_id)
        self.require_role(storage_id, user_id, ("owner",))
        self.repo.soft_delete(storage)
