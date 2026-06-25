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


def _setup(db: Session, owner: User) -> tuple[Storage, str]:
    storage = Storage(name="Share Storage", owner_id=owner.id, storage_type="global")
    db.add(storage)
    db.flush()
    db.add(StorageMember(storage_id=storage.id, user_id=owner.id, role="owner"))
    db.add(StoragePolicy(storage_id=storage.id))
    db.commit()
    db.refresh(storage)
    return storage


def test_create_share_link(client: TestClient, db: Session, test_user: User):
    storage = _setup(db, test_user)
    upload = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("share.txt", b"shared data", "text/plain")},
    )
    file_id = upload.json()["id"]

    resp = client.post(
        f"/api/v1/files/{file_id}/share-links",
        json={"expires_in_hours": 48},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "token" in data
    assert data["download_count"] == 0
    assert data["is_revoked"] is False


def test_download_via_share_link(client: TestClient, db: Session, test_user: User):
    storage = _setup(db, test_user)
    upload = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("dl.txt", b"download via link", "text/plain")},
    )
    file_id = upload.json()["id"]

    link_resp = client.post(
        f"/api/v1/files/{file_id}/share-links", json={}
    )
    token = link_resp.json()["token"]

    resp = client.get(f"/api/v1/shared/{token}")
    assert resp.status_code == 200
    assert resp.content == b"download via link"


def test_list_share_links(client: TestClient, db: Session, test_user: User):
    storage = _setup(db, test_user)
    upload = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("list.txt", b"data", "text/plain")},
    )
    file_id = upload.json()["id"]
    client.post(f"/api/v1/files/{file_id}/share-links", json={})
    client.post(f"/api/v1/files/{file_id}/share-links", json={})

    resp = client.get(f"/api/v1/files/{file_id}/share-links")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_revoke_share_link(client: TestClient, db: Session, test_user: User):
    storage = _setup(db, test_user)
    upload = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("rev.txt", b"data", "text/plain")},
    )
    file_id = upload.json()["id"]
    link_resp = client.post(f"/api/v1/files/{file_id}/share-links", json={})
    token = link_resp.json()["token"]

    resp = client.delete(f"/api/v1/share-links/{token}")
    assert resp.status_code == 204

    resp = client.get(f"/api/v1/shared/{token}")
    assert resp.status_code == 410


def test_expired_share_link(client: TestClient, db: Session, test_user: User):
    from datetime import datetime, timedelta, timezone
    from app.models.share_link import ShareLink

    storage = _setup(db, test_user)
    upload = client.post(
        f"/api/v1/storages/{storage.id}/files",
        files={"file": ("exp.txt", b"data", "text/plain")},
    )
    file_id = upload.json()["id"]

    link_resp = client.post(
        f"/api/v1/files/{file_id}/share-links",
        json={"expires_in_hours": 24},
    )
    token = link_resp.json()["token"]

    link = db.query(ShareLink).filter(ShareLink.token == token).first()
    link.expires_at = datetime.now(timezone.utc) - timedelta(hours=1)
    db.commit()

    resp = client.get(f"/api/v1/shared/{token}")
    assert resp.status_code == 410
