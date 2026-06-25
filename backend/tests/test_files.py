import io
import os
import shutil
import tempfile
import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.integrations.local_storage import LocalFileStorage, local_storage
from app.models.file import FileRecord
from app.models.storage import Storage
from app.models.storage_member import StorageMember
from app.models.storage_policy import StoragePolicy
from app.models.user import User


@pytest.fixture(autouse=True)
def temp_storage_dir(tmp_path):
    local_storage.base_path = tmp_path
    yield tmp_path


def _create_storage(db: Session, owner: User) -> Storage:
    storage = Storage(name="File Storage", owner_id=owner.id, storage_type="global")
    db.add(storage)
    db.flush()
    db.add(StorageMember(storage_id=storage.id, user_id=owner.id, role="owner"))
    db.add(StoragePolicy(storage_id=storage.id))
    db.commit()
    db.refresh(storage)
    return storage


def test_upload_file(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    files = {"file": ("test.txt", b"hello world", "text/plain")}
    resp = client.post(f"/api/v1/storages/{storage.id}/files", files=files)
    assert resp.status_code == 201
    data = resp.json()
    assert data["original_name"] == "test.txt"
    assert data["size_bytes"] == 11
    assert data["is_deleted"] is False


def test_list_files(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    files = {"file": ("a.txt", b"aaa", "text/plain")}
    client.post(f"/api/v1/storages/{storage.id}/files", files=files)

    resp = client.get(f"/api/v1/storages/{storage.id}/files")
    assert resp.status_code == 200
    assert len(resp.json()) == 1


def test_download_file(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    upload_resp = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("dl.txt", b"download me", "text/plain")},
    )
    file_id = upload_resp.json()["id"]

    resp = client.get(f"/api/v1/files/{file_id}/download")
    assert resp.status_code == 200
    assert resp.content == b"download me"


def test_rename_file(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    upload_resp = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("old.txt", b"data", "text/plain")},
    )
    file_id = upload_resp.json()["id"]

    resp = client.put(f"/api/v1/files/{file_id}/rename", json={"name": "new.txt"})
    assert resp.status_code == 200
    assert resp.json()["original_name"] == "new.txt"


def test_delete_file(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    upload_resp = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("rm.txt", b"bye", "text/plain")},
    )
    file_id = upload_resp.json()["id"]

    resp = client.delete(f"/api/v1/files/{file_id}")
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/files/{file_id}")
    assert resp.status_code == 404


def test_search_files(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("report.pdf", b"pdf data", "application/pdf")},
    )
    client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("photo.jpg", b"img data", "image/jpeg")},
    )

    resp = client.get(f"/api/v1/storages/{storage.id}/search?q=report")
    assert resp.status_code == 200
    assert len(resp.json()) == 1
    assert resp.json()[0]["original_name"] == "report.pdf"


def test_move_file(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    upload_resp = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("mv.txt", b"move me", "text/plain")},
    )
    file_id = upload_resp.json()["id"]

    folder_resp = client.post(
        f"/api/v1/storages/{storage.id}/folders", json={"name": "subfolder"}
    )
    folder_id = folder_resp.json()["id"]

    resp = client.put(f"/api/v1/files/{file_id}/move", json={"folder_id": folder_id})
    assert resp.status_code == 200
    assert resp.json()["folder_id"] == folder_id
