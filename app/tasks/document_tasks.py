import io
from pypdf import PdfReader
from app.schemas.classification import DocumentClassification
from app.llm import model
import tiktoken

from app.core import config  # load config variables

# Structured LLM for classification
structured_llm = model.with_structured_output(
    DocumentClassification,
    strict=True
)

# Count tokens using model from config
def count_tokens(text: str, model: str = config.LLM_MODEL) -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# Main PDF processing
def basic_tasks(file_bytes: bytes, file_name: str):
    file = io.BytesIO(file_bytes)
    pdf_reader = PdfReader(file)

    # -----------------------
    # Classification using first PREVIEW_PAGES pages
    # -----------------------
    preview_text = ""
    for page in pdf_reader.pages[:config.PREVIEW_PAGES]:
        text = page.extract_text()
        if text:
            preview_text += text + "\n"

    classification_result = structured_llm.invoke(preview_text)
    document_type = classification_result.document_type
    confidence_score = classification_result.confidence_score

    # -----------------------
    # Token counting & cost using all pages
    # -----------------------
    full_text = ""
    for page in pdf_reader.pages[:config.MAX_PAGE]:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    total_tokens = count_tokens(full_text)
    cost = (total_tokens / 1000) * config.COST_PER_1K_TOKENS

    return total_tokens, cost, document_type, confidence_score
