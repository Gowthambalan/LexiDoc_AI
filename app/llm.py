from langchain_openai import ChatOpenAI
from app.core import config


# ===============================
# LLM instance
# ===============================
model = ChatOpenAI(
    model=config.LLM_MODEL,
    temperature=config.LLM_TEMPERATURE,
    api_key=config.OPENAI_API_KEY
)
