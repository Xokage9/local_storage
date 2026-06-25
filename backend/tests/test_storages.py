import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.storage import Storage
from app.models.storage_member import StorageMember
from app.models.storage_policy import StoragePolicy
from app.models.user import User


def _create_storage(db: Session, owner: User, name: str = "Test Storage", storage_type: str = "global") -> Storage:
    storage = Storage(name=name, owner_id=owner.id, storage_type=storage_type)
    db.add(storage)
    db.flush()
    member = StorageMember(storage_id=storage.id, user_id=owner.id, role="owner")
    db.add(member)
    policy = StoragePolicy(storage_id=storage.id)
    db.add(policy)
    db.commit()
    db.refresh(storage)
    return storage


def test_create_storage(client: TestClient):
    resp = client.post("/api/v1/storages", json={"name": "My Storage"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "My Storage"
    assert data["storage_type"] == "global"
    assert data["is_active"] is True


def test_list_storages(client: TestClient, db: Session, test_user: User):
    _create_storage(db, test_user, "Storage One")
    _create_storage(db, test_user, "Storage Two")

    resp = client.get("/api/v1/storages")
    assert resp.status_code == 200
    data = resp.json()
    assert "own" in data
    assert len(data["own"]) >= 2


def test_get_storage(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    resp = client.get(f"/api/v1/storages/{storage.id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "Test Storage"


def test_update_storage(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    resp = client.put(f"/api/v1/storages/{storage.id}", json={"name": "Renamed"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "Renamed"


def test_delete_storage(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    resp = client.delete(f"/api/v1/storages/{storage.id}")
    assert resp.status_code == 204


def test_get_nonexistent_storage(client: TestClient):
    resp = client.get(f"/api/v1/storages/{uuid.uuid4()}")
    assert resp.status_code in (403, 404)


def test_storage_stats(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    resp = client.get(f"/api/v1/storages/{storage.id}/stats")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_files"] == 0
    assert data["total_size_bytes"] == 0
