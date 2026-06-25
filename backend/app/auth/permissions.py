import uuid

from sqlalchemy.orm import Session

from app.models.storage_member import StorageMember
from app.models.file_access import FileAccess


ROLE_LEVELS = {
    "owner": 5,
    "admin": 4,
    "editor": 3,
    "uploader": 2,
    "viewer": 1,
}


def has_storage_permission(
    db: Session, storage_id: uuid.UUID, user_id: uuid.UUID, min_role: str = "viewer"
) -> bool:
    member = db.query(StorageMember).filter(
        StorageMember.storage_id == storage_id,
        StorageMember.user_id == user_id,
    ).first()
    if not member:
        return False
    return ROLE_LEVELS.get(member.role, 0) >= ROLE_LEVELS.get(min_role, 0)


def has_file_permission(
    db: Session, file_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    access = db.query(FileAccess).filter(
        FileAccess.file_id == file_id,
        FileAccess.user_id == user_id,
    ).first()
    return access is not None
