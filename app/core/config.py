import os
from dotenv import load_dotenv

load_dotenv()

#==========================
#REDIS
#==========================

REDIS_URI: str = os.getenv("REDIS_URI")
if not REDIS_URI:
    raise RuntimeError("REDIS_URI is not set in environment variables")

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_DB = int(os.getenv("REDIS_DB"))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)

#==========================
#Database
#==========================

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# Model and cost configuration

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", 0.0))
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY is not set in environment variables")

# Cost configuration
INPUT_COST_PER_1K = float(os.getenv("INPUT_COST_PER_1K"))
OUTPUT_COST_PER_1K = float(os.getenv("OUTPUT_COST_PER_1K"))

# Qdrant settings
QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = int(os.getenv("QDRANT_PORT"))
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION")

# Embedding model
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# ===============================
# PDF processing
# ===============================
PREVIEW_PAGES = int(os.getenv("PREVIEW_PAGES"))
MAX_PAGE = int(os.getenv("MAX_PAGE"))


# ===============================
# LLM / tokenization
# ===============================
LLM_MODEL = os.getenv("LLM_MODEL")
COST_PER_1K_TOKENS = float(os.getenv("COST_PER_1K_TOKENS"))


# ===============================
# JWT / Authentication
# ===============================
SECRET_KEY = os.getenv("SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
)
REFRESH_TOKEN_EXPIRE_DAYS = int(
    os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")
)

# Safety check
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set in environment variables")


# ===============================
# Password hashing
# ===============================
BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS"))
