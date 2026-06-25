import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_audit_service,
    get_current_user,
    get_db,
    get_storage_repo,
    get_user_repo,
)
from app.auth.jwt_validator import validate_token
from app.models.storage_policy import StoragePolicy
from app.models.user import User
from app.repositories.storages import StorageRepository
from app.repositories.users import UserRepository
from app.schemas.audit import AuditEventRead
from app.schemas.storage import StoragePolicyUpdate, StorageRead
from app.schemas.user import UserRead
from app.services.audit_service import AuditService

router = APIRouter(prefix="/admin", tags=["admin"])


def require_admin(user: User = Depends(get_current_user)) -> User:
    if not getattr(user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


@router.get("/users", response_model=list[UserRead])
def list_users(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    user_repo: UserRepository = Depends(get_user_repo),
):
    return user_repo.list_all(offset, limit)


@router.get("/storages", response_model=list[StorageRead])
def list_all_storages(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    storage_repo: StorageRepository = Depends(get_storage_repo),
):
    return storage_repo.list_all(offset, limit)


@router.put("/storages/{storage_id}/policy")
def update_storage_policy(
    storage_id: uuid.UUID,
    body: StoragePolicyUpdate,
    user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    policy = db.query(StoragePolicy).filter(
        StoragePolicy.storage_id == storage_id
    ).first()
    if not policy:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found")

    if body.max_file_size_bytes is not None:
        policy.max_file_size_bytes = body.max_file_size_bytes
    if body.max_storage_bytes is not None:
        policy.max_storage_bytes = body.max_storage_bytes
    if body.allowed_extensions is not None:
        policy.allowed_extensions = body.allowed_extensions
    if body.allowed_mime_types is not None:
        policy.allowed_mime_types = body.allowed_mime_types
    db.commit()
    return {"status": "ok"}


@router.get("/audit", response_model=list[AuditEventRead])
def list_audit_events(
    storage_id: uuid.UUID | None = Query(None),
    user_id: uuid.UUID | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user: User = Depends(require_admin),
    audit: AuditService = Depends(get_audit_service),
):
    return audit.list_events(storage_id, user_id, offset, limit)
