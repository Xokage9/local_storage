import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.folder import Folder


class FolderRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, folder_id: uuid.UUID) -> Folder | None:
        return self.db.get(Folder, folder_id)

    def list_by_storage(
        self, storage_id: uuid.UUID, parent_id: uuid.UUID | None = None
    ) -> list[Folder]:
        stmt = select(Folder).where(
            Folder.storage_id == storage_id,
            Folder.parent_id == parent_id,
        ).order_by(Folder.name)
        return list(self.db.scalars(stmt).all())

    def create(
        self,
        storage_id: uuid.UUID,
        name: str,
        created_by: uuid.UUID,
        parent_id: uuid.UUID | None = None,
    ) -> Folder:
        folder = Folder(
            storage_id=storage_id,
            name=name,
            parent_id=parent_id,
            created_by=created_by,
        )
        self.db.add(folder)
        self.db.flush()
        return folder

    def rename(self, folder: Folder, name: str) -> Folder:
        folder.name = name
        self.db.flush()
        return folder

    def delete(self, folder: Folder) -> None:
        self.db.delete(folder)
        self.db.flush()

    def get_children_recursive(self, folder_id: uuid.UUID) -> list[Folder]:
        result = []
        children = list(
            self.db.scalars(
                select(Folder).where(Folder.parent_id == folder_id)
            ).all()
        )
        for child in children:
            result.append(child)
            result.extend(self.get_children_recursive(child.id))
        return result
