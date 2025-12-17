

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


GEN_PROMPT = ChatPromptTemplate.from_template("""
You are a legal document analysis assistant.

Based on the context provided below, answer the user's question accurately and thoroughly.

IMPORTANT INSTRUCTIONS:
- Analyze the entire context carefully, even if it's lengthy
- Provide specific information from the context when available
- Quote relevant sections when appropriate
- If the information is partially available, provide what you can find
- Only say "Not mentioned in the document" if the information is truly absent after careful analysis
- Be thorough in your search through the context before concluding information is missing

Context:
{context}

Question:
{question}

Answer (be detailed and specific):
""")

def retrieve(state: AgentState):
    """Retrieve relevant context from vector store"""
    try:
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
        print(f"Retrieved {len(results)} documents")
        for i, doc in enumerate(results):
            print(f"Document {i+1} preview: {doc.page_content[:200]}...")
            
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
    
    # Debug: Show what's being sent to LLM
    print(f"\n=== Context being sent to LLM ===")
    print(f"Length: {len(context_text)} characters")
    print(f"First 500 chars: {context_text[:500]}...")
    print(f"Question: {state['question']}")
    print("=" * 50 + "\n")

    try:
        # Format the prompt
        formatted_prompt = GEN_PROMPT.format(
            context=context_text,
            question=state['question']
        )
        
        # Call the LLM
        response = model.invoke(formatted_prompt)
        
        print(f"Generated response: {response.content}")
        state['answer'] = response.content
        
    except Exception as e:
        print(f"Error generating answer: {e}")
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
