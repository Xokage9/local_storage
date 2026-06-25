import uuid

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.storage import Storage
from app.models.storage_member import StorageMember
from app.models.storage_policy import StoragePolicy
from app.models.user import User


def _create_storage_with_owner(db: Session, owner: User) -> Storage:
    storage = Storage(name="ACL Storage", owner_id=owner.id, storage_type="global")
    db.add(storage)
    db.flush()
    db.add(StorageMember(storage_id=storage.id, user_id=owner.id, role="owner"))
    db.add(StoragePolicy(storage_id=storage.id))
    db.commit()
    db.refresh(storage)
    return storage


def test_list_members(client: TestClient, db: Session, test_user: User):
    storage = _create_storage_with_owner(db, test_user)
    resp = client.get(f"/api/v1/storages/{storage.id}/members")
    assert resp.status_code == 200
    members = resp.json()
    assert len(members) == 1
    assert members[0]["role"] == "owner"


def test_add_member(client: TestClient, db: Session, test_user: User, second_user: User):
    storage = _create_storage_with_owner(db, test_user)
    resp = client.post(
        f"/api/v1/storages/{storage.id}/members",
        json={"user_id": str(second_user.id), "role": "viewer"},
    )
    assert resp.status_code == 201
    assert resp.json()["role"] == "viewer"


def test_update_member_role(client: TestClient, db: Session, test_user: User, second_user: User):
    storage = _create_storage_with_owner(db, test_user)
    db.add(StorageMember(storage_id=storage.id, user_id=second_user.id, role="viewer"))
    db.commit()

    resp = client.put(
        f"/api/v1/storages/{storage.id}/members/{second_user.id}",
        json={"role": "editor"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "editor"


def test_remove_member(client: TestClient, db: Session, test_user: User, second_user: User):
    storage = _create_storage_with_owner(db, test_user)
    db.add(StorageMember(storage_id=storage.id, user_id=second_user.id, role="viewer"))
    db.commit()

    resp = client.delete(f"/api/v1/storages/{storage.id}/members/{second_user.id}")
    assert resp.status_code == 204


def test_non_admin_cannot_add_member(client_second_user: TestClient, db: Session, test_user: User, second_user: User):
    storage = _create_storage_with_owner(db, test_user)
    db.add(StorageMember(storage_id=storage.id, user_id=second_user.id, role="viewer"))
    db.commit()

    third_id = uuid.uuid4()
    resp = client_second_user.post(
        f"/api/v1/storages/{storage.id}/members",
        json={"user_id": str(third_id), "role": "viewer"},
    )
    assert resp.status_code == 403
