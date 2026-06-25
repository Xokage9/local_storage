import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class Folder(Base):
    __tablename__ = "folders"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    storage_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("storages.id"), nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("folders.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    created_by: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)

    storage = relationship("Storage", back_populates="folders")
    parent = relationship("Folder", remote_side="Folder.id", backref="children")
    creator = relationship("User", foreign_keys=[created_by])
