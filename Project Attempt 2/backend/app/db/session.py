from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.settings import settings


class Base(DeclarativeBase):
    pass


_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        connect_args = {}
        if settings.database_url.startswith("sqlite"):
            connect_args = {"check_same_thread": False}
        _engine = create_engine(settings.database_url, echo=False, future=True, connect_args=connect_args)
    return _engine


def get_session_local():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=get_engine())
    return _SessionLocal


def seed_default_users() -> None:
    """Create a default admin and voter for local/dev convenience."""
    from sqlalchemy.orm import Session

    from app.core.security import hash_password
    from app.models.user import User

    SessionLocal = get_session_local()
    db: Session = SessionLocal()
    try:
        if db.query(User).count() == 0:
            admin = User(
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                role="ADMIN",
                voter_type="FACULTY",
                is_eligible=True,
            )
            voter = User(
                email="voter@example.com",
                password_hash=hash_password("voter123"),
                role="VOTER",
                voter_type="STUDENT",
                is_eligible=True,
            )
            db.add_all([admin, voter])
            db.commit()
    finally:
        db.close()


def init_db() -> None:
    # Import models to register with metadata
    from app.models import user, election, candidate, vote, audit  # noqa: F401

    Base.metadata.create_all(bind=get_engine())
    seed_default_users()


def db_session():
    Session = get_session_local()
    db = Session()
    try:
        yield db
    finally:
        db.close()
