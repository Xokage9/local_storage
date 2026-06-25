from fastapi.testclient import TestClient


def test_get_auth_config(client: TestClient):
    resp = client.get("/api/v1/auth/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "auth_url" in data
    assert "token_url" in data
    assert "client_id" in data


def test_get_me(client: TestClient):
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["display_name"] == "Test User"
    assert data["is_active"] is True


def test_get_me_returns_user_id(client: TestClient):
    resp = client.get("/api/v1/auth/me")
    data = resp.json()
    assert "id" in data
    assert "keycloak_id" in data
