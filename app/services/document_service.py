from sqlalchemy.orm import Session
from app.db.models import Document, DocumentMeta
from app.services.vector_db import update_document_type_in_vector_db
from typing import Optional

# --------------------------------------------------
# Get Documents By User
# --------------------------------------------------
def get_documents_by_user(user_id: int, db: Session):
    """
    Returns all documents uploaded by a specific user, ordered by upload time descending.
    """
    return (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.uploaded_time.desc())
        .all()
    )


# --------------------------------------------------
# Get Document Metadata
# --------------------------------------------------
def get_document_metadata(file_id: int, db: Session):
    """
    Returns metadata for a specific document.
    Includes filename, uploaded_time, classified_class.
    """
    return (
        db.query(
            Document.filename,
            Document.uploaded_time,
            Document.classified_class
        )
        .filter(Document.id == file_id)
        .first()
    )


# --------------------------------------------------
# Update Document Metadata
# --------------------------------------------------
def update_document_metadata(
    file_id: int,
    data,
    db: Session
) -> Optional[Document]:
    """
    Updates document metadata in both Document and DocumentMeta tables.
    If classified_class changes, also updates vector DB.
    """
    document = db.query(Document).filter(Document.id == file_id).first()
    if not document:
        return None

    classified_class_updated = False

    # -------------------------
    # Update Document table
    # -------------------------
    if hasattr(data, "filename") and data.filename is not None:
        document.filename = data.filename

    if hasattr(data, "classified_class") and data.classified_class is not None:
        document.classified_class = data.classified_class
        classified_class_updated = True

    if hasattr(data, "uploaded_time") and data.uploaded_time is not None:
        document.uploaded_time = data.uploaded_time

    # -------------------------
    # Update DocumentMeta table
    # -------------------------
    meta = db.query(DocumentMeta).filter(DocumentMeta.file_id == file_id).first()
    if not meta:
        meta = DocumentMeta(file_id=file_id)
        db.add(meta)

    if hasattr(data, "court") and data.court is not None:
        meta.court = data.court

    if hasattr(data, "petitioner") and data.petitioner is not None:
        meta.petitioners = data.petitioner

    if hasattr(data, "respondents") and data.respondents is not None:
        meta.respondents = data.respondents

    db.commit()
    db.refresh(document)

    # -------------------------
    # Update Vector DB if needed
    # -------------------------
    if classified_class_updated:
        update_document_type_in_vector_db(
            document_id=file_id,
            new_document_type=data.classified_class
        )

    return document
