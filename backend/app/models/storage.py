import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class Storage(Base):
    __tablename__ = "storages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    storage_type: Mapped[str] = mapped_column(String(20), nullable=False)
    disk_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    owner = relationship("User", back_populates="storages", lazy="selectin")
    members = relationship("StorageMember", back_populates="storage", cascade="all, delete-orphan", lazy="selectin")
    folders = relationship("Folder", back_populates="storage", cascade="all, delete-orphan", lazy="selectin")
    files = relationship("FileRecord", back_populates="storage", cascade="all, delete-orphan", lazy="selectin")
    policy = relationship("StoragePolicy", back_populates="storage", uselist=False, cascade="all, delete-orphan", lazy="selectin")
