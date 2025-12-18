
import redis
import json
from typing import Optional


r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

def get_session(session_id: str) -> Optional[dict]:
    """
    Retrieve a chat session from Redis.
    Returns a dictionary with 'chat_history'.
    """
    data = r.get(session_id)
    if data:
        return json.loads(data) 
    return None

def save_session(session_id: str, session_state: dict):
    """
    Save or update a chat session in Redis.
    """
    r.set(session_id, json.dumps(session_state))
