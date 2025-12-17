from fastapi import APIRouter,HTTPException,UploadFile,Form,Depends
from uuid import uuid4
from sqlalchemy.orm import Session
import os 
from app.db.deps import get_db
from app.db.models import Document
from app.services.vector_db import convert_bytes_documents


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

        new_doc = Document(
            user_id=user_id,
            filename=file.filename,
            status="Queue",
            classified_status=False,

        )

        db.add(new_doc)
        db.commit()
        db.refresh(new_doc)

        uploaded_files.append({
            "file_id": new_doc.id,
            "file_name": file.filename,
            "status": "Queue"
        })
        convert_bytes_documents(file_bytes,file.filename,new_doc.id)






    return {
        "message": "Files uploaded successfully",
        "status": "Queue",
        "files": uploaded_files
    }
