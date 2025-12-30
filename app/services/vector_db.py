# ===============================
# imports
# ===============================
import io
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

from app.schemas.classification import DocumentClassification
from app.llm import model
from app.core import config  # load config variables


# ===============================
# Initialize Embeddings & Vector Store
# ===============================
embeddings_model = OpenAIEmbeddings(model=config.EMBEDDING_MODEL)

vector_store = QdrantVectorStore.from_documents(
    documents=[],  # start empty
    embedding=embeddings_model,
    url=f"http://{config.QDRANT_HOST}:{config.QDRANT_PORT}",
    collection_name=config.QDRANT_COLLECTION
)

# Structured output LLM
structured_llm = model.with_structured_output(
    DocumentClassification,
    strict=True
)

# Qdrant client
qdrant_client = QdrantClient(host=config.QDRANT_HOST, port=config.QDRANT_PORT)


# ===============================
# Functions
# ===============================
def convert_bytes_documents(file_bytes: bytes, file_name: str, doc_id: int, document_type: str, confidence_score: float):
    """
    Convert PDF bytes into Document objects, store in Qdrant vector DB.

    Args:
        file_bytes (bytes): PDF file in bytes
        file_name (str): Name of the file
        doc_id (int): Unique document ID
        document_type (str): Type/classification of the document
        confidence_score (float): Confidence score of classification

    Returns:
        List[Document]: List of LangChain Document objects
    """
    file = io.BytesIO(file_bytes)
    pdf_reader = PdfReader(file)
    docs = []

    for page_num, page in enumerate(pdf_reader.pages):
        if page_num >= config.MAX_PAGE:
            break

        text = page.extract_text()
        if not text:
            continue

        docs.append(
            Document(
                page_content=text,
                metadata={
                    "source": file_name,
                    "page": page_num + 1,
                    "document_id": doc_id,
                    "document_type": document_type,
                    "confidence_score": confidence_score,
                }
            )
        )

    # Store in Qdrant
    if docs:
        vector_store.add_documents(docs)

    return docs


def update_document_type_in_vector_db(document_id: int, new_document_type: str):
    """
    Update the 'document_type' field in Qdrant vector DB for a given document ID.

    Args:
        document_id (int): Document ID to update
        new_document_type (str): New document type value
    """
    # Scroll through points matching document_id
    results = qdrant_client.scroll(
        collection_name=config.QDRANT_COLLECTION,
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
    )

    points = results[0] if results else []

    for point in points:
        metadata = point.payload.get('metadata', {})
        metadata['document_type'] = new_document_type

        qdrant_client.set_payload(
            collection_name=config.QDRANT_COLLECTION,
            payload={"metadata": metadata},
            points=[point.id]
        )
