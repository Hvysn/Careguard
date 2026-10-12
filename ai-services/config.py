import os
from pydantic_settings import BaseSettings if "BaseSettings" in globals() else object

class Settings:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_DIR = os.path.join(BASE_DIR, "data", "sample_policies")
    CHROMA_PERSIST_DIR = os.path.join(BASE_DIR, "data", "chroma_db")

    # Embedding setup: defaults to local sentence-transformers (zero API keys needed)
    EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "huggingface")
    HUGGINGFACE_EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"

    # LLM setup
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o-mini")
    LLM_TEMPERATURE = 0.0

    # Chunking & Retrieval
    CHUNK_SIZE = 800
    CHUNK_OVERLAP = 150
    TOP_K = 4

settings = Settings()
