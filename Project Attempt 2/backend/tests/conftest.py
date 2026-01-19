import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def client(tmp_path_factory: pytest.TempPathFactory):
    tmp = tmp_path_factory.mktemp("db")
    db_path = tmp / "test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["JWT_SECRET"] = "test-secret"

    # Import after env vars are set
    from app.main import app

    # Startup event seeds users
    with TestClient(app) as c:
        yield c


def login(client: TestClient, email: str, password: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    resp.raise_for_status()
    return resp.json()["access_token"]


@pytest.fixture()
def admin_token(client: TestClient) -> str:
    return login(client, "admin@example.com", "admin123")


@pytest.fixture()
def voter_token(client: TestClient) -> str:
    return login(client, "voter@example.com", "voter123")
