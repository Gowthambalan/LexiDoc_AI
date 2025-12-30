from pydantic import BaseModel
from typing import Optional, Literal
from datetime import datetime

# ----------------------------
# Document List Response
# ----------------------------

class DocumentListResponse(BaseModel):
    file_id: int
    filename: str
    classified_status: bool
    status: str
    classified_class: Optional[str] = None

    class Config:
        from_attributes = True


# ----------------------------
# Get Metadata Response
# ----------------------------

class DocumentMetadataResponse(BaseModel):
    filename: str
    uploaded_time: datetime
    classified_class: Optional[str] = None

    class Config:
        from_attributes = True


# ----------------------------
# Update Metadata Schema
# ----------------------------

ClassifiedClass = Literal[
    "Court Order",
    "Affidavit",
    "Petition",
    "Contract",
    "Notice"
]

class DocumentMetadataUpdate(BaseModel):
    filename: Optional[str] = None
    classified_class: Optional[ClassifiedClass] = None
    court: Optional[str] = None
    uploaded_time: Optional[datetime] = None
    petitioner: Optional[str] = None
    respondents: Optional[str] = None
