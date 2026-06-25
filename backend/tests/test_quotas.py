import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.integrations.local_storage import local_storage
from app.models.storage import Storage
from app.models.storage_member import StorageMember
from app.models.storage_policy import StoragePolicy
from app.models.user import User


@pytest.fixture(autouse=True)
def temp_storage_dir(tmp_path):
    local_storage.base_path = tmp_path
    yield tmp_path


def _create_storage_with_policy(
    db: Session, owner: User, max_file_size: int = 1024, max_storage: int = 4096
) -> Storage:
    storage = Storage(name="Quota Storage", owner_id=owner.id, storage_type="global")
    db.add(storage)
    db.flush()
    db.add(StorageMember(storage_id=storage.id, user_id=owner.id, role="owner"))
    db.add(StoragePolicy(
        storage_id=storage.id,
        max_file_size_bytes=max_file_size,
        max_storage_bytes=max_storage,
    ))
    db.commit()
    db.refresh(storage)
    return storage


def test_upload_within_quota(client: TestClient, db: Session, test_user: User):
    storage = _create_storage_with_policy(db, test_user, max_file_size=1024, max_storage=4096)
    resp = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("small.txt", b"x" * 100, "text/plain")},
    )
    assert resp.status_code == 201


def test_upload_exceeds_file_size_limit(client: TestClient, db: Session, test_user: User):
    storage = _create_storage_with_policy(db, test_user, max_file_size=50, max_storage=4096)
    resp = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("big.txt", b"x" * 100, "text/plain")},
    )
    assert resp.status_code == 413


def test_upload_exceeds_storage_quota(client: TestClient, db: Session, test_user: User):
    storage = _create_storage_with_policy(db, test_user, max_file_size=1024, max_storage=100)
    client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("fill.txt", b"x" * 80, "text/plain")},
    )
    resp = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("over.txt", b"x" * 80, "text/plain")},
    )
    assert resp.status_code == 413


def test_storage_stats_after_upload(client: TestClient, db: Session, test_user: User):
    storage = _create_storage_with_policy(db, test_user)
    client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("a.txt", b"x" * 200, "text/plain")},
    )
    resp = client.get(f"/api/v1/storages/{storage.id}/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_files"] == 1
    assert data["total_size_bytes"] == 200
