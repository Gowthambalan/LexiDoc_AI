

from typing_extensions import TypedDict, List
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from app.core.redis_checkpoint import checkpointer
from qdrant_client.models import Filter, FieldCondition, MatchValue
from app.services.vector_db import vector_store
from app.llm import model


class AgentState(TypedDict):
    question: str
    file_id: str
    context: List[Document]
    answer: str
    chat_history:List[dict]

# Prompt for initial document summary (used only on upload)
SUMMARY_PROMPT = ChatPromptTemplate.from_template("""
You are a legal document analysis assistant.

Based on the document metadata and context provided, create a professional summary of the document.

Document Metadata:
{metadata}

Document Context:
{context}

Provide a summary in the following format:

I've analyzed this document. [Brief description of what the document is - be specific about the type, parties involved, date, court, etc.]

Key Findings:
- Document Type: [type]
- Confidence: [confidence]%
- Document Name:[source]

Would you like me to extract more specific details or summarize the ruling?

Be professional and concise. Extract specific details from the metadata and context.
""")


GEN_PROMPT = ChatPromptTemplate.from_template("""
You are a legal document analysis assistant.

Based on the context provided below, answer the user's question accurately and thoroughly.

IMPORTANT INSTRUCTIONS:
- Analyze the entire context carefully, even if it's lengthy
- Provide specific information from the context when available
- Quote relevant sections when appropriate
- If the user refers to previous questions or answers, use the chat history
- If the information is partially available, provide what you can find
- Only say "Not mentioned in the document" if the information is truly absent after careful analysis
- Be thorough in your search through the context before concluding information is missing

Conversation History:
{chat_history}
                                                                                       ]
Context:
{context}

Question:
{question}

Answer (be detailed and specific):
""")

def retrieve(state: AgentState):
    """Retrieve relevant context from vector store"""
    try:
        if state['question'].lower()=='explain':
            state['question']="Explain a summry of the document"
     
        results = vector_store.similarity_search(
            state['question'],
            k=5,  # Increased from 3 to get more context
            filter=Filter(
                must=[
                    FieldCondition(
                        key="metadata.document_id",
                        match=MatchValue(value=int(state['file_id']))  # Ensure correct type
                    )
                ]
            )
        )
        state['context'] = results

        # Better debug output
        # print(f"Retrieved {len(results)} documents")
        # for i, doc in enumerate(results):
        #     print(f"Document {i+1} preview: {doc.page_content[:200]}...")

    except Exception as e:
        print(f"Error retrieving context: {e}")
        state['context'] = []

    return state


def generation(state: AgentState):
    """Generate answer from context"""
    if not state['context']:
        state['answer'] = "No relevant context found in the document."
        return state
    
    # Join page content with clear separators
    context_parts = []
    for i, doc in enumerate(state['context'], 1):
        context_parts.append(f"--- Section {i} ---\n{doc.page_content}")

    context_text = "\n\n".join(context_parts)

    #meta data joining
    metadata_dict = state['context'][0].metadata if state['context'] else {}
      
    meta_data=[]
    for key,value in metadata_dict.items():
            if key  in ["source","document_type","confidence_score"]:
                meta_data.append(f"{key}:{value}")
    metadata_text = "\n".join(meta_data) if meta_data else "No metadata available"


    
    

    #history 
    chat_history_text=""
    if state.get("chat_history"):
        history=[]
        for msg in state['chat_history']:
            role=msg['role']
            content=msg['content']
            history.append(f"{role}:{content}")

        chat_history_text="\n".join(history)
    else:
        chat_history_text=""

    # # Debug: Show what's being sent to LLM
    # print(f"\n=== Context being sent to LLM ===")
    # print(f"Length: {len(context_text)} characters")
    # print(f"First 500 chars: {context_text[:500]}...")
    # print(f"Question: {state['question']}")
    # print("=" * 50 + "\n")

    try:
        # Format the prompt
        if state['question']=="Explain a summry of the document":
        # print(state['context'][0])
        
            formatted_prompt = SUMMARY_PROMPT.format(
                        metadata=metadata_text,
                        context=context_text  
                    )
        else:
            formatted_prompt = GEN_PROMPT.format(
                context=context_text,
                question=state['question'],
                chat_history=chat_history_text
            )

        # Call the LLM
        response = model.invoke(formatted_prompt)

        # print(f"Generated response: {response.content}")
        state['answer'] = response.content

    except Exception as e:
        # print(f"Error generating answer: {e}")
        state['answer'] = f"Error generating answer: {str(e)}"

    return state


graph = StateGraph(AgentState)

graph.add_node("retrieve", retrieve)
graph.add_node("generation", generation)

graph.set_entry_point("retrieve")
graph.add_edge("retrieve", "generation")
graph.add_edge("generation", END)

# Compile graph with Redis checkpoint
# rag_app = graph.compile(checkpointer=checkpointer)
rag_app = graph.compile(
    checkpointer=checkpointer
)
 