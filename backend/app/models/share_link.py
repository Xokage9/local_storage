import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class ShareLink(Base):
    __tablename__ = "share_links"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("files.id"), nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    max_downloads: Mapped[int | None] = mapped_column(Integer, nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, default=0)
    is_revoked: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    file = relationship("FileRecord", back_populates="share_links")
    creator = relationship("User", foreign_keys=[created_by])
