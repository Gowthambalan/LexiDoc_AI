from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    input: str
    file_id: int
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    context: str
    session_id: str
    file_id: int
