from pydantic import BaseModel,Field
from typing import Literal

class DocumentClassification(BaseModel):
    document_type : Literal["Court Order","Affidavit","Petition","Contract","Notice"] = Field(
        description=(
            """
    Classifies the file based on the document type

"""
        )
    )
    confidence_score:float =Field(
        ge=0.0,le=1.0,
        description="Confidence score of the classification (0 to 1)")
