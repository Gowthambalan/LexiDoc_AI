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

#maximum pages 
MAX_PAGE=10

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

def convert_bytes_documents(file_bytes: bytes, file_name: str, doc_id,document_type,confidence_score):
    file = io.BytesIO(file_bytes)
    file_reader = PdfReader(file)

    # full_text = ""
    # for page in file_reader.pages[:2]:
    #     text = page.extract_text()
    #     if text:
    #         full_text += text + "\n"

    # classification_result = structured_llm.invoke(full_text)

    docs = []
    for page_num, page in enumerate(file_reader.pages):
        if page_num<MAX_PAGE:
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
                    },
                )
            )

    # Store in Qdrant
    vector_store.add_documents(docs)


    return docs



# ===========================

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

qdrant_client = QdrantClient(host="localhost", port=6333)

COLLECTION_NAME = "legal_pages"


def update_document_type_in_vector_db(
    document_id: int,
    new_document_type: str
):
    # print('it enter to the update vectore db function file_id and new_document_type',document_id,new_document_type)
    results = qdrant_client.scroll(
        collection_name="legal_pages",
        scroll_filter=Filter(
            must=[
                FieldCondition(
                    key="metadata.document_id",
                    match=MatchValue(value=document_id)
                )
            ]
        ),

    )
    
    points=results[0]
    # print('here is the points of :',points)
    
    # if not points:
    #     print(f"No points found with document_id = {new_document_type}")
    #     return
    

    point_ids=[point.id for point in points]
    
    for point in points:
        
       

        metadata = point.payload.get('metadata')
        

        metadata['document_type']=new_document_type

        qdrant_client.set_payload(
            collection_name="legal_pages",
            payload={"metadata": metadata},
            points=[point.id]
        )
    