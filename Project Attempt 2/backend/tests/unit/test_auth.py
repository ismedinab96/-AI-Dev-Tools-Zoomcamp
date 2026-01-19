from fastapi.testclient import TestClient


def test_login_success(client: TestClient):
    r = client.post("/auth/login", json={"email": "admin@example.com", "password": "admin123"})
    assert r.status_code == 200
    body = r.json()
    assert "access_token" in body


def test_login_fail(client: TestClient):
    r = client.post("/auth/login", json={"email": "admin@example.com", "password": "wrong"})
    assert r.status_code == 401
