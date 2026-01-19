from datetime import datetime
from pydantic import BaseModel

class AuditEventOut(BaseModel):
    id: str
    type: str
    created_at: datetime
    payload: dict
