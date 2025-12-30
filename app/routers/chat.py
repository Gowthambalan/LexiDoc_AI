
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from uuid import uuid4
from time import time
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.db.models import Chat
from app.services.redis_service import get_session, save_session
from app.core.rag_graph import rag_app
import tiktoken
from app.utils.auth import get_current_user
from app.db.models import User

router = APIRouter(tags=['Chat'])

class ChatRequest(BaseModel):

    input: str
    file_id: int
    session_id: str = None

class ChatResponse(BaseModel):
    context: str
    session_id: str
    file_id: int
INPUT_COST_PER_1K = 0.002  # adjust as per your model
OUTPUT_COST_PER_1K = 0.002

def count_tokens(text: str, model_name="gpt-4o-mini") -> int:
    """Counts the number of tokens for a text."""
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))


@router.post("/chat", response_model=ChatResponse)
def chat_endpoint(payload: ChatRequest, db: Session = Depends(get_db),current_user: int = Depends(get_current_user)):

    start_time=time()  

    session_id=payload.session_id or str(uuid4())
    # print("the session id is ",session_id)
    session_state = get_session(session_id) or {"chat_history": []}
    # print("session stat  is :",session_state)
    config = {'configurable': {'thread_id': session_id}}
    result_state=rag_app.invoke({"question":payload.input,"file_id":payload.file_id,"chat_history":session_state.get("chat_history", [])},config=config)
    answer=result_state.answer if hasattr(result_state, "answer") else result_state["answer"]
    # answer = result_state.get("answer", "No answer generated.")
    # print(answer)
    session_state["chat_history"].append({"role": "user", "content": payload.input})
    session_state["chat_history"].append({"role": "assistant", "content": answer})
    save_session(session_id, session_state)

    response_time = time() - start_time

    #token counter
    input_tokens=count_tokens(payload.input)
    output_tokens=count_tokens(answer)
    cost = (input_tokens / 1000) * INPUT_COST_PER_1K + (output_tokens / 1000) * OUTPUT_COST_PER_1K

    user = db.query(User).filter(User.email == current_user).first()
    chat_entry =Chat(
        user_id=user.id,
        session_id=session_id,
        content=session_state["chat_history"], 
        qtoken=input_tokens,
        atoken=output_tokens,
        cost=cost,
        response_time=response_time
    )
    db.add(chat_entry)
    db.commit()
    db.refresh(chat_entry)

    return ChatResponse(
        context=answer,
        session_id=session_id,
        file_id=payload.file_id
    )




