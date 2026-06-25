import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_access_service,
    get_audit_service,
    get_current_user,
    get_db,
    get_member_repo,
    get_quota_service,
    get_storage_service,
)
from app.models.user import User
from app.repositories.members import MemberRepository
from app.schemas.member import MemberCreate, MemberRead, MemberUpdate
from app.schemas.storage import StorageCreate, StorageRead, StorageStats, StorageUpdate
from app.services.access_service import AccessService
from app.services.audit_service import AuditService
from app.services.quota_service import QuotaService
from app.services.storage_service import StorageService

router = APIRouter(tags=["storages"])


@router.get("/storages", response_model=dict)
def list_storages(
    user: User = Depends(get_current_user),
    svc: StorageService = Depends(get_storage_service),
):
    result = svc.list_user_storages(user.id)
    return {
        "own": [StorageRead.model_validate(s) for s in result["own"]],
        "shared": [StorageRead.model_validate(s) for s in result["shared"]],
        "global": [StorageRead.model_validate(s) for s in result["global"]],
    }


@router.post("/storages", response_model=StorageRead, status_code=201)
def create_storage(
    body: StorageCreate,
    user: User = Depends(get_current_user),
    svc: StorageService = Depends(get_storage_service),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    username = user.display_name or user.email.split("@")[0]
    storage = svc.create_storage(body.name, user.id, body.storage_type, username=username)
    audit.log("storage_created", user_id=user.id, storage_id=storage.id)
    db.commit()
    return storage


@router.get("/storages/{storage_id}", response_model=StorageRead)
def get_storage(
    storage_id: uuid.UUID,
    user: User = Depends(get_current_user),
    svc: StorageService = Depends(get_storage_service),
    access: AccessService = Depends(get_access_service),
):
    access.check_storage_access(storage_id, user.id)
    return svc.get_storage(storage_id)


@router.put("/storages/{storage_id}", response_model=StorageRead)
def update_storage(
    storage_id: uuid.UUID,
    body: StorageUpdate,
    user: User = Depends(get_current_user),
    svc: StorageService = Depends(get_storage_service),
    db: Session = Depends(get_db),
):
    storage = svc.update_storage(storage_id, user.id, name=body.name)
    db.commit()
    return storage


@router.delete("/storages/{storage_id}", status_code=204)
def delete_storage(
    storage_id: uuid.UUID,
    user: User = Depends(get_current_user),
    svc: StorageService = Depends(get_storage_service),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    svc.delete_storage(storage_id, user.id)
    audit.log("storage_deleted", user_id=user.id, storage_id=storage_id)
    db.commit()


@router.get("/storages/{storage_id}/stats", response_model=StorageStats)
def get_storage_stats(
    storage_id: uuid.UUID,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    quota: QuotaService = Depends(get_quota_service),
):
    access.check_storage_access(storage_id, user.id)
    return quota.get_usage(storage_id)


# --- Members ---


@router.get("/storages/{storage_id}/members", response_model=list[MemberRead])
def list_members(
    storage_id: uuid.UUID,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    member_repo: MemberRepository = Depends(get_member_repo),
):
    access.check_storage_access(storage_id, user.id)
    return member_repo.list_by_storage(storage_id)


@router.post("/storages/{storage_id}/members", response_model=MemberRead, status_code=201)
def add_member(
    storage_id: uuid.UUID,
    body: MemberCreate,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    member_repo: MemberRepository = Depends(get_member_repo),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    access.check_storage_access(storage_id, user.id, min_role="admin")
    member = member_repo.add(storage_id, body.user_id, body.role, granted_by=user.id)
    audit.log(
        "member_added",
        user_id=user.id,
        storage_id=storage_id,
        details={"target_user": str(body.user_id), "role": body.role},
    )
    db.commit()
    return member


@router.put("/storages/{storage_id}/members/{user_id}", response_model=MemberRead)
def update_member(
    storage_id: uuid.UUID,
    user_id: uuid.UUID,
    body: MemberUpdate,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    member_repo: MemberRepository = Depends(get_member_repo),
    db: Session = Depends(get_db),
):
    access.check_storage_access(storage_id, user.id, min_role="admin")
    member = member_repo.get(storage_id, user_id)
    if not member:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    member_repo.update_role(member, body.role)
    db.commit()
    return member


@router.delete("/storages/{storage_id}/members/{user_id}", status_code=204)
def remove_member(
    storage_id: uuid.UUID,
    user_id: uuid.UUID,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    member_repo: MemberRepository = Depends(get_member_repo),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    access.check_storage_access(storage_id, user.id, min_role="admin")
    member = member_repo.get(storage_id, user_id)
    if not member:
        from fastapi import HTTPException, status
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
    member_repo.remove(member)
    audit.log(
        "member_removed",
        user_id=user.id,
        storage_id=storage_id,
        details={"target_user": str(user_id)},
    )
    db.commit()
