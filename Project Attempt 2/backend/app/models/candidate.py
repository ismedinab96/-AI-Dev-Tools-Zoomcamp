import uuid

from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base

class Candidate(Base):
    __tablename__ = "candidates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    election_id: Mapped[str] = mapped_column(String(36), ForeignKey("elections.id", ondelete="CASCADE"), index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    manifesto: Mapped[str] = mapped_column(String(4000), nullable=False)
    photo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
