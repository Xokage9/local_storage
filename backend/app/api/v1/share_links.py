import uuid
from urllib.parse import quote

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_access_service,
    get_audit_service,
    get_current_user,
    get_db,
    get_file_service,
    get_share_link_service,
)
from app.models.user import User
from app.schemas.share_link import ShareLinkCreate, ShareLinkRead
from app.services.access_service import AccessService
from app.services.audit_service import AuditService
from app.services.file_service import FileService
from app.services.share_link_service import ShareLinkService

router = APIRouter(tags=["share-links"])


@router.post("/files/{file_id}/share-links", response_model=ShareLinkRead, status_code=201)
def create_share_link(
    file_id: uuid.UUID,
    body: ShareLinkCreate,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    file_svc: FileService = Depends(get_file_service),
    svc: ShareLinkService = Depends(get_share_link_service),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    record = file_svc.get_file(file_id)
    access.check_storage_access(record.storage_id, user.id, min_role="editor")
    link = svc.create_link(file_id, user.id, body.expires_in_hours, body.max_downloads)
    audit.log(
        "share_link_created",
        user_id=user.id,
        file_id=file_id,
        details={"token": link.token},
    )
    db.commit()
    return link


@router.get("/files/{file_id}/share-links", response_model=list[ShareLinkRead])
def list_share_links(
    file_id: uuid.UUID,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    file_svc: FileService = Depends(get_file_service),
    svc: ShareLinkService = Depends(get_share_link_service),
):
    record = file_svc.get_file(file_id)
    access.check_storage_access(record.storage_id, user.id)
    return svc.list_by_file(file_id)


@router.delete("/share-links/{token}", status_code=204)
def revoke_share_link(
    token: str,
    user: User = Depends(get_current_user),
    svc: ShareLinkService = Depends(get_share_link_service),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    svc.revoke(token, user.id)
    audit.log("share_link_revoked", user_id=user.id, details={"token": token})
    db.commit()


@router.get("/shared/{token}")
def download_shared_file(
    token: str,
    svc: ShareLinkService = Depends(get_share_link_service),
    file_svc: FileService = Depends(get_file_service),
    audit: AuditService = Depends(get_audit_service),
    db: Session = Depends(get_db),
):
    link = svc.get_by_token(token)
    chunks, filename, mime_type, size = file_svc.stream_file(link.file_id)
    svc.record_download(link)
    audit.log("shared_download", file_id=link.file_id, details={"token": token})
    db.commit()
    return StreamingResponse(
        chunks,
        media_type=mime_type or "application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(filename)}",
            "Content-Length": str(size),
        },
    )
