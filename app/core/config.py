"""
Configuration file for HR Bot
Loads settings from environment variables and defaults
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ============================================
# LLM Provider — controls which LangChain model is used
# "litellm" (default) | "ollama"
# ============================================
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "litellm")

# ============================================
# LLM Configuration - LiteLLM Proxy (primary)
# ============================================
LITELLM_BASE_URL  = os.getenv("LLM_BASE_URL",    "https://litellm-proxy-dev.blackocean-6e308bcc.centralindia.azurecontainerapps.io/")
LITELLM_MODEL     = os.getenv("LLM_MODEL_NAME",  "azure/gpt-4o")
LITELLM_API_KEY   = os.getenv("LLM_API_KEY",     "sk-litellm-proxy-key")

# ============================================
# LLM Configuration - Ollama (fallback)
# ============================================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL",    "llama3")

# ── Phase 2: Azure OpenAI (uncomment when ready) ────────────────────────────
# AZURE_OPENAI_ENDPOINT  = os.getenv("AZURE_OPENAI_ENDPOINT", "")
# AZURE_OPENAI_API_KEY   = os.getenv("AZURE_OPENAI_API_KEY", "")
# AZURE_DEPLOYMENT_NAME  = os.getenv("AZURE_DEPLOYMENT_NAME", "gpt-4o")
# AZURE_API_VERSION      = os.getenv("AZURE_API_VERSION", "2024-02-01")

# ============================================
# Vector Database Paths  (relative to project root)
# ============================================
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "data/embeddings/faiss.index")
ID_TO_CHUNK_PATH = os.getenv("ID_TO_CHUNK_PATH", "data/embeddings/id_to_chunk.json")

# ============================================
# Embedding Model
# ============================================
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

# ============================================
# Search Parameters
# ============================================
TOP_K = int(os.getenv("TOP_K", "4"))                                  # Number of chunks to retrieve
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.3"))  # Min similarity score

# ============================================
# Short-Term Memory (STM) — token budget
# ============================================
MAX_STM_TOKENS = int(os.getenv("MAX_STM_TOKENS", "1000"))  # Max tokens kept in LangChain STM

# ============================================
# API Settings
# ============================================
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# ============================================
# Data Paths
# ============================================
RAW_DOCS_DIR = os.getenv("RAW_DOCS_DIR", "data/raw_docs")
PROCESSED_CHUNKS_DIR = os.getenv("PROCESSED_CHUNKS_DIR", "data/processed_chunks")
METADATA_DIR = os.getenv("METADATA_DIR", "data/metadata")
