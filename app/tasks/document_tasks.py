# from app.db.deps import get_db
# from app.db.database import SessionLocal
# from sqlalchemy.orm import Session
from pypdf import PdfReader
import io
from langchain_core.documents import Document
from app.schemas.classification import DocumentClassification
from app.llm import model
import tiktoken
# from time import time


import tiktoken

def count_tokens(text: str, model: str = "gpt-4o-mini") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))
COST_PER_1K_TOKENS = 0.00015  



structured_llm = model.with_structured_output(
    DocumentClassification,
    strict=True
)

def basic_tasks(file_bytes: bytes, file_name: str):



 
    file = io.BytesIO(file_bytes)
    file_reader = PdfReader(file)

    full_text = ""
    for page in file_reader.pages[:2]:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    classification_result = structured_llm.invoke(full_text)

    full_text = ""
    for page in file_reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    total_tokens = count_tokens(full_text)
    cost = (total_tokens / 1000) * COST_PER_1K_TOKENS

    return total_tokens,cost,classification_result.document_type,classification_result.confidence_score
    



