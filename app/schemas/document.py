# doc-list/{user-id}

from pydantic import BaseModel
from typing import Optional,Literal
from datetime import datetime

class DocumentListResponse(BaseModel):
    file_id: int
    filename: str
    classified_status: bool
    status: str
    classified_class: Optional[str] = None  

    class Config:
        from_attributes = True


#get-metadata/{file_id}/


# class DocumentMetadataResponse(BaseModel):
#     filename: str
#     court: Optional[str] = None
#     uploaded_time: datetime
#     folder_path: Optional[str] = None

#     class Config:
#         from_attributes = True

class DocumentMetadataResponse(BaseModel):
    filename: str
    uploaded_time: datetime
    classified_class: Optional[str] = None
    # court: Optional[str] = None

    class Config:
        from_attributes = True

#update-metadata/{file_id}
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