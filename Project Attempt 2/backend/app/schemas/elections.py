from datetime import datetime
from pydantic import BaseModel

class ElectionOut(BaseModel):
    id: str
    name: str
    starts_at: datetime
    ends_at: datetime
    status: str

class CreateElectionRequest(BaseModel):
    name: str
    starts_at: datetime
    ends_at: datetime
