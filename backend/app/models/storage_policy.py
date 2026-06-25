import uuid

from sqlalchemy import BigInteger, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, generate_uuid


class StoragePolicy(Base):
    __tablename__ = "storage_policies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid)
    storage_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("storages.id"), unique=True, nullable=False
    )
    max_file_size_bytes: Mapped[int] = mapped_column(BigInteger, default=1_073_741_824)  # 1 ГБ
    max_storage_bytes: Mapped[int] = mapped_column(BigInteger, default=3_221_225_472)  # 3 ГБ
    allowed_extensions: Mapped[list | None] = mapped_column(JSON, nullable=True)
    allowed_mime_types: Mapped[list | None] = mapped_column(JSON, nullable=True)

    storage = relationship("Storage", back_populates="policy")
