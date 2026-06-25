import uuid
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class FileRecord(Base):
    __tablename__ = "files"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    storage_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("storages.id"), nullable=False)
    folder_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("folders.id"), nullable=True)
    original_name: Mapped[str] = mapped_column(String(500), nullable=False)
    stored_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    mime_type: Mapped[str | None] = mapped_column(String(255), nullable=True)
    size_bytes: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    uploaded_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    storage = relationship("Storage", back_populates="files")
    folder = relationship("Folder")
    uploader = relationship("User", foreign_keys=[uploaded_by])
    share_links = relationship("ShareLink", back_populates="file", cascade="all, delete-orphan")
    access_entries = relationship("FileAccess", back_populates="file", cascade="all, delete-orphan")
