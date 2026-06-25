import uuid

from urllib.parse import quote

from fastapi import APIRouter, Depends, Query, Request, UploadFile
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_access_service,
    get_audit_service,
    get_current_user,
    get_db,
    get_file_service,
)
from app.models.user import User
from app.schemas.file import FileAccessCreate, FileAccessRead, FileMove, FileRead, FileRename
from app.services.access_service import AccessService
from app.services.audit_service import AuditService
from app.services.file_service import FileService

router = APIRouter(tags=["files"])


@router.get("/storages/{storage_id}/files", response_model=list[FileRead])
def list_files(
    storage_id: uuid.UUID,
    folder_id: uuid.UUID | None = Query(None),
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FileService = Depends(get_file_service),
):
    access.check_storage_access(storage_id, user.id)
    return svc.list_files(storage_id, folder_id)


@router.get("/storages/{storage_id}/search", response_model=list[FileRead])
def search_files(
    storage_id: uuid.UUID,
    q: str = Query(..., min_length=1),
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FileService = Depends(get_file_service),
):
    access.check_storage_access(storage_id, user.id)
    return svc.search_files(storage_id, q)


@router.post("/storages/{storage_id}/files", response_model=FileRead, status_code=201)
async def upload_file(
    storage_id: uuid.UUID,
    file: UploadFile,
    folder_id: uuid.UUID | None = Query(None),
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FileService = Depends(get_file_service),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
    request: Request = None,
):
    access.check_storage_access(storage_id, user.id, min_role="uploader")
    record = await svc.upload_file(storage_id, folder_id, file, user.id)
    audit.log(
        "file_uploaded",
        user_id=user.id,
        storage_id=storage_id,
        file_id=record.id,
        details={"filename": record.original_name, "size": record.size_bytes},
        ip_address=request.client.host if request and request.client else None,
    )
    db.commit()
    return record


@router.get("/files/{file_id}", response_model=FileRead)
def get_file_info(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FileService = Depends(get_file_service),
):
    record = svc.get_file(file_id)
    try:
        access.check_storage_access(record.storage_id, user.id)
    except Exception:
        fa = access.check_file_access(file_id, user.id)
        if not fa:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access")
    return record


@router.get("/files/{file_id}/download")
def download_file(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FileService = Depends(get_file_service),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
    request: Request = None,
):
    record = svc.get_file(file_id)
    try:
        access.check_storage_access(record.storage_id, user.id)
    except Exception:
        fa = access.check_file_access(file_id, user.id)
        if not fa:
            from fastapi import HTTPException, status
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No access")

    chunks, filename, mime_type, size = svc.stream_file(file_id)
    audit.log(
        "file_downloaded",
        user_id=user.id,
        storage_id=record.storage_id,
        file_id=file_id,
        ip_address=request.client.host if request and request.client else None,
    )
    db.commit()
    return StreamingResponse(
        chunks,
        media_type=mime_type or "application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}",
            "Content-Length": str(size),
        },
    )


@router.put("/files/{file_id}/rename", response_model=FileRead)
def rename_file(
    file_id: uuid.UUID,
    body: FileRename,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FileService = Depends(get_file_service),
    db: Session = Depends(get_db),
):
    record = svc.get_file(file_id)
    access.check_storage_access(record.storage_id, user.id, min_role="editor")
    record = svc.rename_file(file_id, body.name)
    db.commit()
    return record


@router.put("/files/{file_id}/move", response_model=FileRead)
def move_file(
    file_id: uuid.UUID,
    body: FileMove,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FileService = Depends(get_file_service),
    db: Session = Depends(get_db),
):
    record = svc.get_file(file_id)
    access.check_storage_access(record.storage_id, user.id, min_role="editor")
    record = svc.move_file(file_id, body.folder_id)
    db.commit()
    return record


@router.delete("/files/{file_id}", status_code=204)
def delete_file(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FileService = Depends(get_file_service),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    record = svc.get_file(file_id)
    access.check_storage_access(record.storage_id, user.id, min_role="editor")
    svc.delete_file(file_id)
    audit.log("file_deleted", user_id=user.id, storage_id=record.storage_id, file_id=file_id)
    db.commit()




@router.get("/files/{file_id}/access", response_model=list[FileAccessRead])
def list_file_access(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    access_svc: AccessService = Depends(get_access_service),
    svc: FileService = Depends(get_file_service),
):
    record = svc.get_file(file_id)
    access_svc.check_storage_access(record.storage_id, user.id, min_role="admin")
    return access_svc.list_file_access(file_id)


@router.post("/files/{file_id}/access", response_model=FileAccessRead, status_code=201)
def grant_file_access(
    file_id: uuid.UUID,
    body: FileAccessCreate,
    user: User = Depends(get_current_user),
    access_svc: AccessService = Depends(get_access_service),
    svc: FileService = Depends(get_file_service),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    record = svc.get_file(file_id)
    access_svc.check_storage_access(record.storage_id, user.id, min_role="admin")
    fa = access_svc.grant_file_access(file_id, body.user_id, body.permission, user.id)
    audit.log(
        "file_access_granted",
        user_id=user.id,
        file_id=file_id,
        details={"target_user": str(body.user_id), "permission": body.permission},
    )
    db.commit()
    return fa


@router.delete("/files/{file_id}/access/{target_user_id}", status_code=204)
def revoke_file_access(
    file_id: uuid.UUID,
    target_user_id: uuid.UUID,
    user: User = Depends(get_current_user),
    access_svc: AccessService = Depends(get_access_service),
    svc: FileService = Depends(get_file_service),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    record = svc.get_file(file_id)
    access_svc.check_storage_access(record.storage_id, user.id, min_role="admin")
    access_svc.revoke_file_access(file_id, target_user_id)
    audit.log(
        "file_access_revoked",
        user_id=user.id,
        file_id=file_id,
        details={"target_user": str(target_user_id)},
    )
    db.commit()
