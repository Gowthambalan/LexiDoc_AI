from fastapi import APIRouter, Depends, HTTPException
from uuid import uuid4
from time import time
from sqlalchemy.orm import Session
import tiktoken

from app.schemas.chat import ChatRequest, ChatResponse
from app.db.deps import get_db
from app.db.models import Chat, User
from app.services.redis_service import get_session, save_session
from app.core.rag_graph import rag_app
from app.utils.auth import get_current_user
from app.core.config import (
    INPUT_COST_PER_1K,
    OUTPUT_COST_PER_1K,
    LLM_MODEL_NAME
)

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

# ----------------------------
# Utility: Token Counter
# ----------------------------

def count_tokens(text: str, model_name: str = LLM_MODEL_NAME) -> int:
    try:
        encoding = tiktoken.encoding_for_model(model_name)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


# ----------------------------
# Chat Endpoint
# ----------------------------

@router.post("/", response_model=ChatResponse)
def chat_endpoint(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
):
    start_time = time()

    # ----------------------------
    # Session Handling (Redis)
    # ----------------------------
    session_id = payload.session_id or str(uuid4())

    session_state = get_session(session_id) or {"chat_history": []}

    config = {
        "configurable": {
            "thread_id": session_id
        }
    }

    # ----------------------------
    # RAG Invocation
    # ----------------------------
    result_state = rag_app.invoke(
        {
            "question": payload.input,
            "file_id": payload.file_id,
            "chat_history": session_state["chat_history"],
        },
        config=config,
    )

    answer = (
        result_state.answer
        if hasattr(result_state, "answer")
        else result_state.get("answer", "No answer generated.")
    )

    # ----------------------------
    # Update Session History
    # ----------------------------
    session_state["chat_history"].extend([
        {"role": "user", "content": payload.input},
        {"role": "assistant", "content": answer},
    ])

    save_session(session_id, session_state)

    # ----------------------------
    # Metrics
    # ----------------------------
    response_time = time() - start_time
    input_tokens = count_tokens(payload.input)
    output_tokens = count_tokens(answer)

    cost = (
        (input_tokens / 1000) * INPUT_COST_PER_1K
        + (output_tokens / 1000) * OUTPUT_COST_PER_1K
    )

    # ----------------------------
    # Store Chat in DB
    # ----------------------------
    user = db.query(User).filter(User.email == current_user).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    chat_entry = Chat(
        user_id=user.id,
        session_id=session_id,
        content=session_state["chat_history"],
        qtoken=input_tokens,
        atoken=output_tokens,
        cost=cost,
        response_time=response_time,
    )

    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)

    # ----------------------------
    # Response
    # ----------------------------
    return ChatResponse(
        context=answer,
        session_id=session_id,
        file_id=payload.file_id,
    )
