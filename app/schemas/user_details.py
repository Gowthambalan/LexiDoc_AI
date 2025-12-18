from pydantic import BaseModel
from datetime import datetime

class UserDetailsOut(BaseModel):
    username: str
    email: str
    role: str | None
    status: str
    last_login: datetime | None
    docs_processed: int

    class Config:
        from_attributes = True
