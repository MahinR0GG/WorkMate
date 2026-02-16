"""
Configuration file for HR Bot
Loads settings from environment variables and defaults
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# LLM Configuration - Ollama
# ============================================
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDO54dX7vF4-Cg0y2i8eOqfhpN-d9_A_kI")  # Commented out - using Ollama now
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")

# ============================================
# Vector Database Paths
# ============================================
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "embeddings/faiss_index.bin")
ID_TO_CHUNK_PATH = os.getenv("ID_TO_CHUNK_PATH", "embeddings/id_to_chunk.json")

# ============================================
# Embedding Model
# ============================================
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ============================================
# Search Parameters
# ============================================
TOP_K = int(os.getenv("TOP_K", "4"))  # Number of chunks to retrieve
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))  # Min similarity score (IndexFlatIP range: -1 to 1)

# ============================================
# API Settings
# ============================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
