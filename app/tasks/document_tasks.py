# from celery import Task
# from sqlalchemy.orm import Session
# from app.db.database import SessionLocal
# from app.db.models import Document
# from app.services.classification_service import classify_document
# from langchain_openai import OpenAIEmbeddings
# from langchain_community.document_loaders import PyPDFLoader
# import tiktoken
# import os
# from dotenv import load_dotenv
# # from app.tasks.celery import celery_app
# import celery_app
# load_dotenv()


# EMBEDDING_MODEL = "text-embedding-3-small" 
# EMBEDDING_COST_PER_1K_TOKENS = 0.00002 

# embeddings =OpenAIEmbeddings(model=EMBEDDING_MODEL)


# def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
#     """Count tokens in text using tiktoken"""
#     try:
#         encoding = tiktoken.encoding_for_model(model)
#         return len(encoding.encode(text))
#     except Exception:
#         # Fallback to cl100k_base encoding (used by GPT-4)
#         encoding = tiktoken.get_encoding("cl100k_base")
#         return len(encoding.encode(text))


# def calculate_embedding_cost(tokens: int) -> float:
#     """Calculate cost for embeddings based on token count"""
#     return (tokens / 1000) * EMBEDDING_COST_PER_1K_TOKENS


# @celery_app.task(bind=True, name="app.tasks.document_tasks.classify_documents")
# def classify_documents(self: Task):

#     db: Session = SessionLocal()
    
#     try:
#         # Find documents with classified_status=False
#         unclassified_docs = db.query(Document).filter(
#             Document.classified_status == False
#         ).all()
        
#         if not unclassified_docs:
#             return {"message": "No documents to classify", "count": 0}
        
#         processed_count = 0
        
#         for doc in unclassified_docs:
#             try:
#                 # Update classified_state to "inprogress" and status to "InProgress"
#                 doc.classified_state = "inprogress"
#                 doc.status = "InProgress"
#                 db.commit()
#                 db.refresh(doc)
                
#                 # Get file path - assuming files are stored in a directory
#                 # You may need to adjust this based on your file storage setup
#                 upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
#                 file_path = os.path.join(upload_dir, f"{doc.id}_{doc.filename}")
                
#                 # Check if file exists
#                 if not os.path.exists(file_path):
#                     # If file doesn't exist, mark as failed
#                     doc.classified_state = "failed"
#                     doc.status = "Failed"
#                     db.commit()
#                     continue
                
#                 # Load PDF to get text for embedding calculation
#                 loader = PyPDFLoader(file_path)
#                 pages = loader.load()
                
#                 if not pages:
#                     doc.classified_state = "failed"
#                     doc.status = "Failed"
#                     db.commit()
#                     continue
                
#                 # Get text from first 2 pages for classification
#                 text = "\n".join([p.page_content for p in pages[:2]])
                
#                 # Count tokens for the text used in classification
#                 classification_tokens = count_tokens(text)
                
#                 # Generate embeddings for the full document (or first few pages)
#                 # For cost calculation, we'll use the full text
#                 full_text = "\n".join([p.page_content for p in pages])
                
#                 # Generate embeddings (this will make API call to OpenAI)
#                 # The embeddings are generated in batches, and we count tokens for cost
#                 embedding_tokens = count_tokens(full_text)
                
#                 # Actually generate embeddings (optional - if you want to store them)
#                 # embedding_vectors = embeddings.embed_documents([full_text])
                
#                 # Calculate embedding cost
#                 embedding_cost = calculate_embedding_cost(embedding_tokens)
                
#                 # Classify the document (this updates the document in DB)
#                 classify_document(doc.id, file_path)
                
#                 # Refresh document to get updated values
#                 db.refresh(doc)
                
#                 # Update token count and cost
#                 doc.token = embedding_tokens
#                 doc.cost = embedding_cost
#                 doc.classified_state = "completed"
#                 doc.status = "Classified"
                
#                 db.commit()
#                 processed_count += 1
                
#             except Exception as e:
#                 # Mark document as failed on error
#                 db.rollback()
#                 doc_id = doc.id  # Save doc.id before potential scope issues
#                 failed_doc = db.query(Document).filter(Document.id == doc_id).first()
#                 if failed_doc:
#                     failed_doc.classified_state = "failed"
#                     failed_doc.status = "Failed"
#                     db.commit()
                
#                 # Log error but continue with other documents
#                 print(f"Error processing document {doc_id}: {str(e)}")
#                 continue
        
#         return {
#             "message": f"Processed {processed_count} documents",
#             "count": processed_count
#         }
        
#     except Exception as e:
#         db.rollback()
#         raise e
#     finally:
#         db.close()
