from pydantic import BaseModel

class CandidateOut(BaseModel):
    id: str
    election_id: str
    full_name: str
    manifesto: str
    photo_url: str | None = None

class CreateCandidateRequest(BaseModel):
    full_name: str
    manifesto: str
    photo_url: str | None = None
