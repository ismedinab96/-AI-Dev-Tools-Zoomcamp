from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient


def auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_vote_only_once(client: TestClient, admin_token: str, voter_token: str):
    now = datetime.now(timezone.utc)
    payload = {
        "name": "Election 2026",
        "starts_at": now.isoformat(),
        "ends_at": (now + timedelta(days=1)).isoformat(),
    }
    r = client.post("/elections", json=payload, headers=auth_header(admin_token))
    assert r.status_code == 201
    election_id = r.json()["id"]

    c1 = client.post(
        f"/elections/{election_id}/candidates",
        json={"full_name": "Alice", "manifesto": "More buses"},
        headers=auth_header(admin_token),
    )
    assert c1.status_code == 201
    candidate_id = c1.json()["id"]

    ropen = client.post(f"/elections/{election_id}/open", headers=auth_header(admin_token))
    assert ropen.status_code == 200

    v1 = client.post(
        f"/elections/{election_id}/vote",
        json={"candidate_id": candidate_id},
        headers=auth_header(voter_token),
    )
    assert v1.status_code == 201

    v2 = client.post(
        f"/elections/{election_id}/vote",
        json={"candidate_id": candidate_id},
        headers=auth_header(voter_token),
    )
    assert v2.status_code == 409
