# doc-list/{user-id}

from sqlalchemy.orm import Session
from app.db.models import Document

def get_documents_by_user(user_id: int, db: Session):
    return (
        db.query(Document)
        .filter(Document.user_id == user_id)
        .order_by(Document.uploaded_time.desc())
        .all()
    )

# get-metadata/{file_id}/

# from sqlalchemy.orm import Session
# from app.db.models import Document, DocumentMeta

# def get_document_metadata(file_id: int, db: Session):
#     return (
#         db.query(
#             Document.filename,
#             Document.uploaded_time,
#             DocumentMeta.court,
#             DocumentMeta.folder_path
#         )
#         .join(DocumentMeta, Document.id == DocumentMeta.file_id)
#         .filter(Document.id == file_id)
#         .first()
#     )


from sqlalchemy.orm import Session
from app.db.models import Document, DocumentMeta

def get_document_metadata(file_id: int, db: Session):
    return (
        db.query(
            Document.filename,
            Document.uploaded_time,
            Document.classified_class,
            DocumentMeta.court
        )
        .join(DocumentMeta, Document.id == DocumentMeta.file_id)
        .filter(Document.id == file_id)
        .first()
    )

#update-metadata/{file_id}

from sqlalchemy.orm import Session
from app.db.models import Document, DocumentMeta
from app.services.vector_db import update_document_type_in_vector_db

# def update_document_metadata(
#     file_id: int,
#     data,
#     db: Session
# ):
#     document = db.query(Document).filter(Document.id == file_id).first()

#     if not document:
#         return None

#     # Update Document table
#     if data.filename is not None:
#         document.filename = data.filename

#     if data.classified_class is not None:
#         document.classified_class = data.classified_class

#     if data.uploaded_time is not None:
#         document.uploaded_time = data.uploaded_time

#     # DocumentMeta table
#     meta = (
#         db.query(DocumentMeta)
#         .filter(DocumentMeta.file_id == file_id)
#         .first()
#     )

#     if not meta:
#         meta = DocumentMeta(file_id=file_id)
#         db.add(meta)

#     if data.court is not None:
#         meta.court = data.court

#     if data.petitioner is not None:
#         meta.petitioners = data.petitioner

#     if data.respondents is not None:
#         meta.respondents = data.respondents

#     db.commit()
#     return document


def update_document_metadata(
    file_id: int,
    data,
    db: Session
):
    document = db.query(Document).filter(Document.id == file_id).first()

    if not document:
        return None

    # Track if classified_class changed
    classified_class_updated = False

    # -------------------------
    # Document table
    # -------------------------
    if data.filename is not None:
        document.filename = data.filename

    if data.classified_class is not None:
        document.classified_class = data.classified_class
        classified_class_updated = True

    if data.uploaded_time is not None:
        document.uploaded_time = data.uploaded_time

    # -------------------------
    # DocumentMeta table
    # -------------------------
    meta = (
        db.query(DocumentMeta)
        .filter(DocumentMeta.file_id == file_id)
        .first()
    )

    if not meta:
        meta = DocumentMeta(file_id=file_id)
        db.add(meta)

    if data.court is not None:
        meta.court = data.court

    if data.petitioner is not None:
        meta.petitioners = data.petitioner

    if data.respondents is not None:
        meta.respondents = data.respondents

    db.commit()

    # -------------------------
    #  Vector DB update
    # -------------------------
    if classified_class_updated:
        update_document_type_in_vector_db(
            document_id=file_id,
            new_document_type=data.classified_class
        )

    return document
