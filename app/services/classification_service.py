# from sqlalchemy.orm import Session
# from langchain_community.document_loaders import PyPDFLoader

# from app.db.database import SessionLocal
# from app.db.models import Document, DocumentMeta
# from app.schemas.classification import DocumentClassification
# from app.llm import llm


# def classify_document(document_id: int, file_path: str) -> None:

#     db: Session =SessionLocal()

#     try:
#         loader =PyPDFLoader(file_path)
#         pages =loader.load()

#         if not pages:
#             raise ValueError("PDF has no readable pages")

#         text = "\n".join([p.page_content for p in pages[:2]])

#         structured_llm = llm.with_structured_output(
#             DocumentClassification,
#             strict=True
#         )

#         result = structured_llm.invoke(text)


#         doc = db.query(Document).filter(Document.id == document_id).first()
#         if not doc:
#             raise ValueError(f"Document {document_id} not found")

#         doc.status = "Classified"
#         doc.classified_status = True
#         doc.confidence = result.confidence_score

       
#         meta = DocumentMeta(
#             file_id=document_id,
#             court=None,
#             petitioners=None,
#             respondents=None,
#             folder_path=file_path,
#         )

#         db.add(meta)
#         db.commit()
#     except Exception as e:
#         db.rollback()

#         # Mark document as failed
#         doc = db.query(Document).filter(Document.id == document_id).first()
#         if doc:
#             doc.status = "Failed"
#             db.commit()

#         raise e

#     finally:
#         db.close()

