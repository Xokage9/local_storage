import uuid

from fastapi import HTTPException, status

from app.models.folder import Folder
from app.repositories.folders import FolderRepository


class FolderService:
    def __init__(self, repo: FolderRepository) -> None:
        self.repo = repo

    def list_folders(
        self, storage_id: uuid.UUID, parent_id: uuid.UUID | None = None
    ) -> list[Folder]:
        return self.repo.list_by_storage(storage_id, parent_id)

    def create_folder(
        self,
        storage_id: uuid.UUID,
        name: str,
        created_by: uuid.UUID,
        parent_id: uuid.UUID | None = None,
    ) -> Folder:
        if parent_id:
            parent = self.repo.get_by_id(parent_id)
            if not parent or parent.storage_id != storage_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Parent folder not found"
                )
        return self.repo.create(storage_id, name, created_by, parent_id)

    def rename_folder(self, folder_id: uuid.UUID, name: str) -> Folder:
        folder = self.repo.get_by_id(folder_id)
        if not folder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
        return self.repo.rename(folder, name)

    def delete_folder(self, folder_id: uuid.UUID) -> None:
        folder = self.repo.get_by_id(folder_id)
        if not folder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
        self.repo.delete(folder)

    def get_folder(self, folder_id: uuid.UUID) -> Folder:
        folder = self.repo.get_by_id(folder_id)
        if not folder:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Folder not found")
        return folder
