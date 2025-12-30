from fastapi import APIRouter,HTTPException,UploadFile,Form,Depends,status
from uuid import uuid4
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.db.models import Document,User
from app.services.vector_db import convert_bytes_documents
from app.tasks.document_tasks import basic_tasks
from datetime import datetime
from typing import List
from app.schemas.document import DocumentListResponse, DocumentMetadataResponse, DocumentMetadataUpdate
from app.services.document_service import get_documents_by_user, get_document_metadata, update_document_metadata
from app.utils.auth import get_current_user

router = APIRouter(tags=["Documents"])


# --------------------------------------------------
# Upload Documents
# --------------------------------------------------

@router.post("/upload",status_code=status.HTTP_201_CREATED)
async def upload_document(
    current_user: str =Depends(get_current_user),
    files: list[UploadFile] = Form(...),
    db: Session = Depends(get_db),
):
    """securtiy added api"""

    user = db.query(User).filter(User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    uploaded_files = []

    for file in files:
        file_bytes = await file.read()
        try:
            total_tokens,cost,document_type,confidence_score=basic_tasks(file_bytes,file.filename)
            status_value="Classified"

        except Exception as e:
            total_tokens=None
            cost=None,
            document_type=None,
            confidence_score=None
            status_value="Error"

        

        new_doc = Document(
            user_id=user.id,
            filename=file.filename,
            classified_status=True,
            classified_class=document_type,
            uploaded_time=datetime.now(),
            status=status_value,
            confidence=confidence_score,
            token=total_tokens,
            cost=cost

        )

        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)
        print(status_value)

        
        if status_value=="Classified":
            convert_bytes_documents(file_bytes,file.filename,new_doc.id,document_type,confidence_score)
        uploaded_files.append({
            "file_id": new_doc.id,
            "file_name": file.filename,
            "status": status_value
        })



    return {
        "message": "Files uploaded successfully",
        "status": status_value,
        "files": uploaded_files
    }

# --------------------------------------------------
# List Documents for Logged-in User
# --------------------------------------------------

@router.get("/doc-list", response_model=List[DocumentListResponse])
def get_document_list(
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user),
):
    "auth added "
    user = db.query(User).filter(User.email == current_user).first()

    documents = get_documents_by_user(user.id, db)

    if not documents:
        raise HTTPException(status_code=404, detail="No documents found")

    return [
        {
            "file_id": doc.id,
            "filename": doc.filename,
            "classified_status": doc.classified_status,
            "status": doc.status,
            "classified_class": doc.classified_class,
        }
        for doc in documents
    ]

# --------------------------------------------------
# Get Document Metadata
# --------------------------------------------------

@router.get(
    "/get-metadata/{file_id}/",
    response_model=DocumentMetadataResponse
)
def get_metadata(
    file_id: int,
    db: Session = Depends(get_db),current_user: int = Depends(get_current_user),
):
    metadata = get_document_metadata(file_id, db)

    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Metadata not found for this file"
        )

    return {
        "filename": metadata.filename,
        # "court": metadata.court,
        "uploaded_time": metadata.uploaded_time,
        # "folder_path": metadata.folder_path,
        "classified_class": metadata.classified_class,
    }

 # --------------------------------------------------
 # Update Document Metadata
# ---------------------------------------------------

@router.put("/update-metadata/{file_id}")
def update_metadata(
    file_id: int,
    payload: DocumentMetadataUpdate,
    db: Session = Depends(get_db),
    current_user: int = Depends(get_current_user)
):
    result = update_document_metadata(file_id, payload, db)

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Document not found"
        )

    return {
        "message": "Metadata updated successfully",
        "file_id": file_id
    }


