from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.storage import Storage
from app.models.storage_member import StorageMember
from app.models.storage_policy import StoragePolicy
from app.models.user import User


def _create_storage(db: Session, owner: User) -> Storage:
    storage = Storage(name="Folder Storage", owner_id=owner.id, storage_type="global")
    db.add(storage)
    db.flush()
    db.add(StorageMember(storage_id=storage.id, user_id=owner.id, role="owner"))
    db.add(StoragePolicy(storage_id=storage.id))
    db.commit()
    db.refresh(storage)
    return storage


def test_create_folder(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    resp = client.post(
        f"/api/v1/storages/{storage.id}/folders", json={"name": "Documents"}
    )
    assert resp.status_code == 201
    assert resp.json()["name"] == "Documents"


def test_list_folders(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    client.post(f"/api/v1/storages/{storage.id}/folders", json={"name": "A"})
    client.post(f"/api/v1/storages/{storage.id}/folders", json={"name": "B"})

    resp = client.get(f"/api/v1/storages/{storage.id}/folders")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_nested_folders(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    parent = client.post(
        f"/api/v1/storages/{storage.id}/folders", json={"name": "Parent"}
    )
    parent_id = parent.json()["id"]

    child = client.post(
        f"/api/v1/storages/{storage.id}/folders",
        json={"name": "Child", "parent_id": parent_id},
    )
    assert child.status_code == 201
    assert child.json()["parent_id"] == parent_id


def test_rename_folder(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    folder = client.post(
        f"/api/v1/storages/{storage.id}/folders", json={"name": "Old Name"}
    )
    folder_id = folder.json()["id"]

    resp = client.put(f"/api/v1/folders/{folder_id}", json={"name": "New Name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "New Name"


def test_delete_folder(client: TestClient, db: Session, test_user: User):
    storage = _create_storage(db, test_user)
    folder = client.post(
        f"/api/v1/storages/{storage.id}/folders", json={"name": "ToDelete"}
    )
    folder_id = folder.json()["id"]

    resp = client.delete(f"/api/v1/folders/{folder_id}")
    assert resp.status_code == 204
