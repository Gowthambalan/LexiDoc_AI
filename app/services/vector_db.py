# # app/services/vector_store_service.py
# from langchain_qdrant import QdrantVectorStore
# from langchain_openai import OpenAIEmbeddings
# from pypdf import PdfReader
# import io
# from langchain_core.documents import Document
# from app.schemas.classification import DocumentClassification
# from app.llm import model


# embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")


# vector_store = QdrantVectorStore.from_existing_collection(
#     embedding=embeddings_model,
#     url="http://localhost:6333",
#     collection_name="legal_pages"
# )


# structured_llm=model.with_structured_output(DocumentClassification,strict=True)
# def convert_bytes_documents(file_bytes, file_name,doc_id):
    
#     file=io.BytesIO(file_bytes)
#     file_reader=PdfReader(file)
#     full_text=''
#     for page in file_reader.pages[:2]:
#         text = page.extract_text()
#         if text:
#             full_text += text + "\n"

#     classification_result=structured_llm.invoke(text)
#     docs=[]
#     for page_num,page in enumerate(file_reader.pages):
#         text=page.extract_text()
#         docs.append(
#             Document(page_content=text,metadata={"source": file_name, "page": page_num + 1,"document_id":doc_id,"document_type":classification_result.document_type,"confidence_score":classification_result.confidence_score})
#         )


#     vector_store.add_documents(docs)
#     return docs
        



from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from pypdf import PdfReader
import io
from langchain_core.documents import Document
from app.schemas.classification import DocumentClassification
from app.llm import model

# Embedding model
embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

#  AUTO-CREATE collection if it does not exist
vector_store = QdrantVectorStore.from_documents(
    documents=[],  # empty on first run
    embedding=embeddings_model,
    url="http://localhost:6333",
    collection_name="legal_pages"
)

# Structured output LLM
structured_llm = model.with_structured_output(
    DocumentClassification,
    strict=True
)

def convert_bytes_documents(file_bytes: bytes, file_name: str, doc_id: str):
    file = io.BytesIO(file_bytes)
    file_reader = PdfReader(file)

    full_text = ""
    for page in file_reader.pages[:2]:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    classification_result = structured_llm.invoke(full_text)

    docs = []
    for page_num, page in enumerate(file_reader.pages):
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
                    "document_type": classification_result.document_type,
                    "confidence_score": classification_result.confidence_score,
                },
            )
        )

    # Store in Qdrant
    vector_store.add_documents(docs)

    return docs



# ===========================

from qdrant_client.models import Filter, FieldCondition, MatchValue
from qdrant_client import QdrantClient

# Qdrant low-level client (needed for payload updates)
qdrant_client = QdrantClient(url="http://localhost:6333")

COLLECTION_NAME = "legal_pages"


def update_document_type_in_vector_db(
    document_id: int,
    new_document_type: str
):
    """
    Update only document_type metadata for all vectors
    belonging to a document_id
    """

    qdrant_client.set_payload(
        collection_name=COLLECTION_NAME,
        payload={
            "metadata.document_type": new_document_type
        },
        points=Filter(
            must=[
                FieldCondition(
                    key="document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        )
    )