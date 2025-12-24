from fastapi import APIRouter,HTTPException,UploadFile,Form,Depends
from uuid import uuid4
from sqlalchemy.orm import Session
import os 
from app.db.deps import get_db
from app.db.models import Document
from app.services.vector_db import convert_bytes_documents
from app.tasks.document_tasks import basic_tasks
from datetime import datetime
from typing import List
from app.schemas.document import DocumentListResponse, DocumentMetadataResponse, DocumentMetadataUpdate
from app.services.document_service import get_documents_by_user, get_document_metadata, update_document_metadata


router = APIRouter(tags=["Documents"])


@router.post("/upload")
async def upload_document(
    user_id: str = Form(...),
    files: list[UploadFile] = Form(...),
    db: Session = Depends(get_db),
):
    uploaded_files = []

    for file in files:
        # file_id = str(uuid4())

        file_bytes = await file.read()
        # new_doc = Document(
        #     user_id=user_id,
        #     filename=file.filename,
        #     classified_status=False,
   
        #     uploaded_time=datetime.now(),
        #     status="Queue",
        #     # confidence=confidence_score,
        #     # token=total_tokens,
        #     # cost=cost

        # )
        # db.add(new_doc)
        # db.commit()
        # db.refresh(new_doc)
        
        try:
            total_tokens,cost,document_type,confidence_score=basic_tasks(file_bytes,file.filename)
            status_value="Classified"

        except Exception as e:
            status_value="Error"

        

        new_doc = Document(
            user_id=user_id,
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

        uploaded_files.append({
            "file_id": new_doc.id,
            "file_name": file.filename,
            "status": status_value
        })
        convert_bytes_documents(file_bytes,file.filename,new_doc.id,document_type,confidence_score)




    return {
        "message": "Files uploaded successfully",
        "status": status_value,
        "files": uploaded_files
    }


@router.get("/doc-list/{user_id}", response_model=List[DocumentListResponse])
def get_document_list(
    user_id: int,
    db: Session = Depends(get_db)
):
    documents = get_documents_by_user(user_id, db)

    if not documents:
        raise HTTPException(
            status_code=404,
            detail="No documents found for this user"
        )

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


@router.get(
    "/get-metadata/{file_id}/",
    response_model=DocumentMetadataResponse
)
def get_metadata(
    file_id: int,
    db: Session = Depends(get_db)
):
    metadata = get_document_metadata(file_id, db)

    if not metadata:
        raise HTTPException(
            status_code=404,
            detail="Metadata not found for this file"
        )

    return {
        "filename": metadata.filename,
        "court": metadata.court,
        "uploaded_time": metadata.uploaded_time,
        # "folder_path": metadata.folder_path,
        "classified_class": metadata.classified_class,
    }


@router.put("/update-metadata/{file_id}")
def update_metadata(
    file_id: int,
    payload: DocumentMetadataUpdate,
    db: Session = Depends(get_db)
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

