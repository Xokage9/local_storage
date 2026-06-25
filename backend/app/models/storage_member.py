import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid

VALID_ROLES = ("owner", "admin", "editor", "viewer", "uploader")


class StorageMember(Base):
    __tablename__ = "storage_members"
    __table_args__ = (
        UniqueConstraint("storage_id", "user_id", name="uq_storage_user"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    storage_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("storages.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)
    granted_by: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    storage = relationship("Storage", back_populates="members")
    user = relationship("User", back_populates="memberships", foreign_keys=[user_id])
    grantor = relationship("User", foreign_keys=[granted_by])
