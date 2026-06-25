import uuid

from fastapi import HTTPException, status

from app.models.file_access import FileAccess
from app.repositories.file_access import FileAccessRepository
from app.repositories.members import MemberRepository

ROLE_HIERARCHY = {
    "owner": 5,
    "admin": 4,
    "editor": 3,
    "uploader": 2,
    "viewer": 1,
}


class AccessService:
    def __init__(
        self, member_repo: MemberRepository, file_access_repo: FileAccessRepository
    ) -> None:
        self.member_repo = member_repo
        self.file_access_repo = file_access_repo

    def check_storage_access(
        self, storage_id: uuid.UUID, user_id: uuid.UUID, min_role: str = "viewer"
    ) -> str:
        member = self.member_repo.get(storage_id, user_id)
        if not member:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="No access to this storage"
            )
        if ROLE_HIERARCHY.get(member.role, 0) < ROLE_HIERARCHY.get(min_role, 0):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permissions"
            )
        return member.role

    def can_read(self, storage_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        member = self.member_repo.get(storage_id, user_id)
        return member is not None

    def can_write(self, storage_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        member = self.member_repo.get(storage_id, user_id)
        if not member:
            return False
        return member.role in ("owner", "admin", "editor", "uploader")

    def can_manage(self, storage_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        member = self.member_repo.get(storage_id, user_id)
        if not member:
            return False
        return member.role in ("owner", "admin")

    def check_file_access(
        self, file_id: uuid.UUID, user_id: uuid.UUID
    ) -> FileAccess | None:
        return self.file_access_repo.get(file_id, user_id)

    def grant_file_access(
        self,
        file_id: uuid.UUID,
        user_id: uuid.UUID,
        permission: str,
        granted_by: uuid.UUID,
    ) -> FileAccess:
        existing = self.file_access_repo.get(file_id, user_id)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Access already granted",
            )
        return self.file_access_repo.grant(file_id, user_id, permission, granted_by)

    def revoke_file_access(self, file_id: uuid.UUID, user_id: uuid.UUID) -> None:
        existing = self.file_access_repo.get(file_id, user_id)
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Access not found"
            )
        self.file_access_repo.revoke(existing)

    def list_file_access(self, file_id: uuid.UUID) -> list[FileAccess]:
        return self.file_access_repo.list_by_file(file_id)
