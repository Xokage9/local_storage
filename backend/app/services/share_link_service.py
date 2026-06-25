import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status

from app.models.share_link import ShareLink
from app.repositories.share_links import ShareLinkRepository


class ShareLinkService:
    def __init__(self, repo: ShareLinkRepository) -> None:
        self.repo = repo

    def create_link(
        self,
        file_id: uuid.UUID,
        created_by: uuid.UUID,
        expires_in_hours: int | None = 24,
        max_downloads: int | None = None,
    ) -> ShareLink:
        token = secrets.token_urlsafe(32)
        expires_at = None
        if expires_in_hours:
            expires_at = datetime.now(timezone.utc) + timedelta(hours=expires_in_hours)

        return self.repo.create(
            token=token,
            file_id=file_id,
            created_by=created_by,
            expires_at=expires_at,
            max_downloads=max_downloads,
        )

    def get_by_token(self, token: str) -> ShareLink:
        link = self.repo.get_by_token(token)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="prosba ne naydena, kak ty cuda popal?))"
            )
        if link.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_410_GONE, detail="Link has been revoked"
            )
        if link.expires_at and link.expires_at.replace(tzinfo=timezone.utc) <= datetime.now(timezone.utc):
            raise HTTPException(
                status_code=status.HTTP_410_GONE, detail="ne uspel, link has expired :("
            )
        if link.max_downloads and link.download_count >= link.max_downloads:
            raise HTTPException(
                status_code=status.HTTP_410_GONE, detail="limit konchilsya, plati 100 rubley))"
            )
        return link

    def record_download(self, link: ShareLink) -> None:
        self.repo.increment_download(link)

    def list_by_file(self, file_id: uuid.UUID) -> list[ShareLink]:
        return self.repo.list_by_file(file_id)

    def revoke(self, token: str, user_id: uuid.UUID) -> None:
        link = self.repo.get_by_token(token)
        if not link:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Share link not found"
            )
        if link.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="no prav bratishka",
            )
        self.repo.revoke(link)
