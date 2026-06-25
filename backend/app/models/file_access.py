import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class FileAccess(Base):
    __tablename__ = "file_access"
    __table_args__ = (
        UniqueConstraint("file_id", "user_id", name="uq_file_user_access"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    file_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("files.id"), nullable=False)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    permission: Mapped[str] = mapped_column(String(20), nullable=False)  # view / download
    granted_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    file = relationship("FileRecord", back_populates="access_entries")
    user = relationship("User", foreign_keys=[user_id])
    grantor = relationship("User", foreign_keys=[granted_by])
