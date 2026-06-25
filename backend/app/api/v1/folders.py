import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_access_service,
    get_current_user,
    get_db,
    get_folder_service,
)
from app.models.user import User
from app.schemas.folder import FolderCreate, FolderRead, FolderRename
from app.services.access_service import AccessService
from app.services.folder_service import FolderService

router = APIRouter(tags=["folders"])


@router.get("/storages/{storage_id}/folders", response_model=list[FolderRead])
def list_folders(
    storage_id: uuid.UUID,
    parent_id: uuid.UUID | None = Query(None),
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FolderService = Depends(get_folder_service),
):
    access.check_storage_access(storage_id, user.id)
    return svc.list_folders(storage_id, parent_id)


@router.post("/storages/{storage_id}/folders", response_model=FolderRead, status_code=201)
def create_folder(
    storage_id: uuid.UUID,
    body: FolderCreate,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FolderService = Depends(get_folder_service),
    db: Session = Depends(get_db),
):
    access.check_storage_access(storage_id, user.id, min_role="editor")
    folder = svc.create_folder(storage_id, body.name, user.id, body.parent_id)
    db.commit()
    return folder


@router.put("/folders/{folder_id}", response_model=FolderRead)
def rename_folder(
    folder_id: uuid.UUID,
    body: FolderRename,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FolderService = Depends(get_folder_service),
    db: Session = Depends(get_db),
):
    folder = svc.get_folder(folder_id)
    access.check_storage_access(folder.storage_id, user.id, min_role="editor")
    folder = svc.rename_folder(folder_id, body.name)
    db.commit()
    return folder


@router.delete("/folders/{folder_id}", status_code=204)
def delete_folder(
    folder_id: uuid.UUID,
    user: User = Depends(get_current_user),
    access: AccessService = Depends(get_access_service),
    svc: FolderService = Depends(get_folder_service),
    db: Session = Depends(get_db),
):
    folder = svc.get_folder(folder_id)
    access.check_storage_access(folder.storage_id, user.id, min_role="editor")
    svc.delete_folder(folder_id)
    db.commit()
