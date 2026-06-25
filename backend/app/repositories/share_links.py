import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.share_link import ShareLink


class ShareLinkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_token(self, token: str) -> ShareLink | None:
        stmt = select(ShareLink).where(ShareLink.token == token)
        return self.db.scalars(stmt).first()

    def get_by_id(self, link_id: uuid.UUID) -> ShareLink | None:
        return self.db.get(ShareLink, link_id)

    def list_by_file(self, file_id: uuid.UUID) -> list[ShareLink]:
        stmt = (
            select(ShareLink)
            .where(ShareLink.file_id == file_id)
            .order_by(ShareLink.created_at.desc())
        )
        return list(self.db.scalars(stmt).all())

    def create(self, **kwargs) -> ShareLink:
        link = ShareLink(**kwargs)
        self.db.add(link)
        self.db.flush()
        return link

    def increment_download(self, link: ShareLink) -> None:
        link.download_count += 1
        self.db.flush()

    def revoke(self, link: ShareLink) -> None:
        link.is_revoked = True
        self.db.flush()
