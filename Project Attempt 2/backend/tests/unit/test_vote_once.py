from datetime import datetime, timedelta, timezone
from fastapi.testclient import TestClient


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_vote_once_per_election(client: TestClient, admin_token: str, voter_token: str):
    # Create election
    now = datetime.now(timezone.utc)
    payload = {"name": "Test Election", "starts_at": now.isoformat(), "ends_at": (now + timedelta(days=1)).isoformat()}
    r = client.post("/elections", json=payload, headers=_auth(admin_token))
    assert r.status_code == 201
    election_id = r.json()["id"]

    # Add candidates
    c1 = client.post(f"/elections/{election_id}/candidates", json={"full_name": "Alice", "manifesto": "A"}, headers=_auth(admin_token))
    assert c1.status_code == 201
    c1_id = c1.json()["id"]

    c2 = client.post(f"/elections/{election_id}/candidates", json={"full_name": "Bob", "manifesto": "B"}, headers=_auth(admin_token))
    assert c2.status_code == 201
    c2_id = c2.json()["id"]

    # Open election
    r = client.post(f"/elections/{election_id}/open", headers=_auth(admin_token))
    assert r.status_code == 200

    # Voter votes
    r = client.post(f"/elections/{election_id}/vote", json={"candidate_id": c1_id}, headers=_auth(voter_token))
    assert r.status_code == 201

    # Second vote should fail with 409
    r = client.post(f"/elections/{election_id}/vote", json={"candidate_id": c2_id}, headers=_auth(voter_token))
    assert r.status_code == 409
