import os
from datetime import datetime, timedelta, timezone
import pytest
from fastapi.testclient import TestClient

pytestmark = pytest.mark.integration


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_workflow(client: TestClient, admin_token: str, voter_token: str):
    # This test uses whatever DATABASE_URL is set (SQLite for local, Postgres for CI)
    now = datetime.now(timezone.utc)
    r = client.post(
        "/elections",
        json={
            "name": "Integration Election",
            "starts_at": now.isoformat(),
            "ends_at": (now + timedelta(days=1)).isoformat(),
        },
        headers=auth_header(admin_token),
    )
    assert r.status_code == 201
    election_id = r.json()["id"]

    c1 = client.post(
        f"/elections/{election_id}/candidates",
        json={"full_name": "Bob", "manifesto": "Lower cafeteria prices"},
        headers=auth_header(admin_token),
    )
    assert c1.status_code == 201

    client.post(f"/elections/{election_id}/open", headers=auth_header(admin_token))

    v = client.post(
        f"/elections/{election_id}/vote",
        json={"candidate_id": c1.json()["id"]},
        headers=auth_header(voter_token),
    )
    assert v.status_code == 201

    client.post(f"/elections/{election_id}/close", headers=auth_header(admin_token))

    res = client.get(f"/elections/{election_id}/results", headers=auth_header(admin_token))
    assert res.status_code == 200
    totals = res.json()["totals"]
    assert sum(t["votes"] for t in totals) == 1
