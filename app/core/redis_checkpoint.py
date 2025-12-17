import os
import redis
from langgraph.checkpoint.redis import RedisSaver

# # Define your Redis URI
# REDIS_HOST = 'localhost'
# REDIS_PORT = 6379
# REDIS_DB = int(os.getenv("REDIS_DB", 0))

# # Create Redis client 
# redis_client = redis.Redis(host= REDIS_HOST, port= REDIS_PORT, db= REDIS_DB)

# # Create Redis based checkpoint 
# checkpointer = RedisSaver(redis_client= redis_client)


# Create Redis persistence
REDIS_URI = "redis://localhost:6379"
with RedisSaver.from_conn_string(REDIS_URI) as checkpointer:
    # Initialize Redis indices (only needed once)
    checkpointer.setup()

