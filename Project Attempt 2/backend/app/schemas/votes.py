from datetime import datetime
from pydantic import BaseModel

class VoteRequest(BaseModel):
    candidate_id: str

class MyVoteResponse(BaseModel):
    election_id: str
    candidate_id: str
    created_at: datetime
