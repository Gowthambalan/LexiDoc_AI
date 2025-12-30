from pydantic import BaseModel
from typing import Optional

class DocumentListRequest(BaseModel):
    search: Optional[str] = None
    status: Optional[str] = None   # Classified / Error
    class_type: Optional[str] = None
