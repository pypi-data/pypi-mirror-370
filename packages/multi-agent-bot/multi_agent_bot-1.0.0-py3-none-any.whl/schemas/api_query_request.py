from pydantic import BaseModel
from typing import Optional


class QueryRequest(BaseModel):
    query: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
