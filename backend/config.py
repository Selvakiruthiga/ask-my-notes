import os
from dotenv import load_dotenv

# Load variables from .env file into the environment
load_dotenv()

# Read the Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Safety check - stops the app early with a clear error if key is missing
if not GEMINI_API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Please add it to your .env file."
    )

# Embedding model name (used later in retriever.py)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_CACHE_DIR = os.getenv("MODEL_CACHE_DIR", "./models")

# Chunking settings (used in document_processor.py)
CHUNK_SIZE = 60      # words per chunk
CHUNK_OVERLAP = 15     # words shared between consecutive chunks

# Retrieval settings (used in retriever.py)
TOP_K_BM25 = 10
TOP_K_SEMANTIC = 10
FINAL_TOP_K = 5        # how many chunks get sent to the LLM

# ChromaDB storage path (used in vector_store.py)
CHROMA_DB_PATH = os.getenv("STORE_PATH", "./data/store")
