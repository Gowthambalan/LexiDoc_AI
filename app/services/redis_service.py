import redis
import json
from typing import Optional
from app.core.config import REDIS_HOST, REDIS_PORT, REDIS_DB, REDIS_PASSWORD

# Create a Redis connection pool
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=True
)

def get_session(session_id: str) -> Optional[dict]:
    """
    Retrieve a chat session from Redis.
    Returns a dictionary with 'chat_history'.
    """
    data = r.get(session_id)
    if data:
        return json.loads(data)
    return None

def save_session(session_id: str, session_state: dict, expire_seconds: int = 86400):
    """
    Save or update a chat session in Redis.
    By default, session expires in 24 hours (86400 seconds).
    """
    r.set(session_id, json.dumps(session_state), ex=expire_seconds)
