import uuid

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.auth.jwt_validator import validate_token
from app.db.session import get_db
from app.integrations.local_storage import LocalFileStorage, local_storage
from app.models.user import User
from app.repositories.audit import AuditRepository
from app.repositories.file_access import FileAccessRepository
from app.repositories.files import FileRepository
from app.repositories.folders import FolderRepository
from app.repositories.members import MemberRepository
from app.repositories.share_links import ShareLinkRepository
from app.repositories.storages import StorageRepository
from app.repositories.users import UserRepository
from app.services.access_service import AccessService
from app.services.audit_service import AuditService
from app.services.file_service import FileService
from app.services.folder_service import FolderService
from app.services.quota_service import QuotaService
from app.services.share_link_service import ShareLinkService
from app.services.storage_service import StorageService

security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    payload = validate_token(credentials.credentials)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token"
        )

    keycloak_id = payload.get("sub")
    if not keycloak_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

    user_repo = UserRepository(db)
    user = user_repo.get_by_keycloak_id(keycloak_id)

    if not user:
        email = payload.get("email", f"{keycloak_id}@local")
        display_name = payload.get("preferred_username") or payload.get("name")
        user = user_repo.create(keycloak_id=keycloak_id, email=email, display_name=display_name)

        username = display_name or email.split("@")[0]
        storage_repo = StorageRepository(db)
        member_repo = MemberRepository(db)
        svc = StorageService(storage_repo, member_repo)
        svc.create_personal_storage(user.id, username)
        db.commit()

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is deactivated")

    return user


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_storage_repo(db: Session = Depends(get_db)) -> StorageRepository:
    return StorageRepository(db)


def get_folder_repo(db: Session = Depends(get_db)) -> FolderRepository:
    return FolderRepository(db)


def get_file_repo(db: Session = Depends(get_db)) -> FileRepository:
    return FileRepository(db)


def get_member_repo(db: Session = Depends(get_db)) -> MemberRepository:
    return MemberRepository(db)


def get_share_link_repo(db: Session = Depends(get_db)) -> ShareLinkRepository:
    return ShareLinkRepository(db)


def get_audit_repo(db: Session = Depends(get_db)) -> AuditRepository:
    return AuditRepository(db)


def get_file_access_repo(db: Session = Depends(get_db)) -> FileAccessRepository:
    return FileAccessRepository(db)


def get_storage_service(
    storage_repo: StorageRepository = Depends(get_storage_repo),
    member_repo: MemberRepository = Depends(get_member_repo),
) -> StorageService:
    return StorageService(storage_repo, member_repo)


def get_folder_service(
    folder_repo: FolderRepository = Depends(get_folder_repo),
) -> FolderService:
    return FolderService(folder_repo)


def get_quota_service(
    db: Session = Depends(get_db),
    file_repo: FileRepository = Depends(get_file_repo),
) -> QuotaService:
    return QuotaService(db, file_repo)


def get_file_service(
    db: Session = Depends(get_db),
    file_repo: FileRepository = Depends(get_file_repo),
    quota_service: QuotaService = Depends(get_quota_service),
) -> FileService:
    return FileService(file_repo, local_storage, quota_service, db=db)


def get_access_service(
    member_repo: MemberRepository = Depends(get_member_repo),
    file_access_repo: FileAccessRepository = Depends(get_file_access_repo),
) -> AccessService:
    return AccessService(member_repo, file_access_repo)


def get_share_link_service(
    repo: ShareLinkRepository = Depends(get_share_link_repo),
) -> ShareLinkService:
    return ShareLinkService(repo)


def get_audit_service(
    repo: AuditRepository = Depends(get_audit_repo),
) -> AuditService:
    return AuditService(repo)
