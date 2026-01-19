from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.deps import get_current_user, require_admin
from app.core.security import create_access_token, verify_password
from app.db.session import db_session
from app.models.user import User
from app.models.election import Election
from app.models.candidate import Candidate
from app.models.vote import Vote
from app.models.audit import AuditEvent
from app.schemas.auth import LoginRequest, TokenResponse, MeResponse
from app.schemas.elections import CreateElectionRequest, ElectionOut
from app.schemas.candidates import CreateCandidateRequest, CandidateOut
from app.schemas.votes import VoteRequest, MyVoteResponse
from app.schemas.results import ResultsResponse, ResultLine
from app.schemas.audit import AuditEventOut

router = APIRouter()


def audit(db: Session, election_id: str, actor_user_id: str | None, typ: str, payload: dict) -> None:
    db.add(AuditEvent(election_id=election_id, actor_user_id=actor_user_id, type=typ, payload=payload))


@router.post("/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(db_session)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).one_or_none()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)) -> MeResponse:
    return MeResponse(id=user.id, email=user.email, role=user.role, voter_type=user.voter_type, is_eligible=user.is_eligible)


@router.get("/elections", response_model=list[ElectionOut])
def list_elections(db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> list[ElectionOut]:
    rows = db.query(Election).order_by(Election.starts_at.desc()).all()
    return [ElectionOut(**r.__dict__) for r in rows]


@router.post("/elections", response_model=ElectionOut, status_code=201)
def create_election(
    payload: CreateElectionRequest,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> ElectionOut:
    e = Election(name=payload.name, starts_at=payload.starts_at, ends_at=payload.ends_at, status="DRAFT")
    db.add(e)
    db.commit()
    db.refresh(e)
    audit(db, e.id, admin.id, "ELECTION_CREATED", {"name": e.name})
    db.commit()
    return ElectionOut(**e.__dict__)


@router.get("/elections/{election_id}", response_model=ElectionOut)
def get_election(election_id: str, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> ElectionOut:
    e = db.get(Election, election_id)
    if e is None:
        raise HTTPException(404, "Election not found")
    return ElectionOut(**e.__dict__)


@router.post("/elections/{election_id}/open")
def open_election(election_id: str, db: Session = Depends(db_session), admin: User = Depends(require_admin)):
    e = db.get(Election, election_id)
    if e is None:
        raise HTTPException(404, "Election not found")
    if e.status == "CLOSED":
        raise HTTPException(400, "Election already closed")
    e.status = "OPEN"
    db.commit()
    audit(db, election_id, admin.id, "ELECTION_OPENED", {})
    db.commit()
    return {"status": "OPEN"}


@router.post("/elections/{election_id}/close")
def close_election(election_id: str, db: Session = Depends(db_session), admin: User = Depends(require_admin)):
    e = db.get(Election, election_id)
    if e is None:
        raise HTTPException(404, "Election not found")
    e.status = "CLOSED"
    db.commit()
    audit(db, election_id, admin.id, "ELECTION_CLOSED", {})
    db.commit()
    return {"status": "CLOSED"}


@router.get("/elections/{election_id}/candidates", response_model=list[CandidateOut])
def list_candidates(election_id: str, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> list[CandidateOut]:
    rows = db.query(Candidate).filter(Candidate.election_id == election_id).order_by(Candidate.full_name.asc()).all()
    return [CandidateOut(**r.__dict__) for r in rows]


@router.post("/elections/{election_id}/candidates", response_model=CandidateOut, status_code=201)
def create_candidate(
    election_id: str,
    payload: CreateCandidateRequest,
    db: Session = Depends(db_session),
    admin: User = Depends(require_admin),
) -> CandidateOut:
    if db.get(Election, election_id) is None:
        raise HTTPException(404, "Election not found")
    c = Candidate(election_id=election_id, full_name=payload.full_name, manifesto=payload.manifesto, photo_url=payload.photo_url)
    db.add(c)
    db.commit()
    db.refresh(c)
    audit(db, election_id, admin.id, "CANDIDATE_CREATED", {"candidate_id": c.id, "full_name": c.full_name})
    db.commit()
    return CandidateOut(**c.__dict__)


@router.post("/elections/{election_id}/vote", status_code=201)
def cast_vote(
    election_id: str,
    payload: VoteRequest,
    db: Session = Depends(db_session),
    user: User = Depends(get_current_user),
):
    if not user.is_eligible:
        raise HTTPException(status_code=403, detail="Not eligible")
    e = db.get(Election, election_id)
    if e is None:
        raise HTTPException(404, "Election not found")
    if e.status != "OPEN":
        raise HTTPException(400, "Election not open")
    c = db.get(Candidate, payload.candidate_id)
    if c is None or c.election_id != election_id:
        raise HTTPException(400, "Invalid candidate")

    v = Vote(election_id=election_id, voter_id=user.id, candidate_id=payload.candidate_id)
    db.add(v)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Already voted")

    audit(db, election_id, user.id, "VOTE_CAST", {"candidate_id": payload.candidate_id})
    db.commit()
    return {"ok": True}


@router.get("/elections/{election_id}/my-vote", response_model=MyVoteResponse)
def my_vote(election_id: str, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> MyVoteResponse:
    v = db.query(Vote).filter(Vote.election_id == election_id, Vote.voter_id == user.id).one_or_none()
    if v is None:
        raise HTTPException(404, "Not found")
    return MyVoteResponse(election_id=v.election_id, candidate_id=v.candidate_id, created_at=v.created_at)


@router.get("/elections/{election_id}/results", response_model=ResultsResponse)
def results(election_id: str, db: Session = Depends(db_session), user: User = Depends(get_current_user)) -> ResultsResponse:
    e = db.get(Election, election_id)
    if e is None:
        raise HTTPException(404, "Election not found")

    rows = (
        db.query(Candidate.id, Candidate.full_name, func.count(Vote.id))
        .outerjoin(Vote, (Vote.candidate_id == Candidate.id) & (Vote.election_id == election_id))
        .filter(Candidate.election_id == election_id)
        .group_by(Candidate.id, Candidate.full_name)
        .order_by(func.count(Vote.id).desc(), Candidate.full_name.asc())
        .all()
    )
    totals = [ResultLine(candidate_id=r[0], full_name=r[1], votes=int(r[2])) for r in rows]
    return ResultsResponse(election_id=e.id, status=e.status, totals=totals)


@router.get("/elections/{election_id}/audit", response_model=list[AuditEventOut])
def audit_log(election_id: str, db: Session = Depends(db_session), admin: User = Depends(require_admin)) -> list[AuditEventOut]:
    rows = db.query(AuditEvent).filter(AuditEvent.election_id == election_id).order_by(AuditEvent.created_at.asc()).all()
    return [AuditEventOut(id=r.id, type=r.type, created_at=r.created_at, payload=r.payload) for r in rows]
