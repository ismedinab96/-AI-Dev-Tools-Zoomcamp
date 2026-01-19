from pydantic import BaseModel

class ResultLine(BaseModel):
    candidate_id: str
    full_name: str
    votes: int

class ResultsResponse(BaseModel):
    election_id: str
    status: str
    totals: list[ResultLine]
