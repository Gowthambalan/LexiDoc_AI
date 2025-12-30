import os
import redis
from langgraph.checkpoint.redis import RedisSaver
from app.core.config import REDIS_URI

with RedisSaver.from_conn_string(REDIS_URI) as checkpointer:
    # Initialize Redis indices (only needed once)
    checkpointer.setup()


