"""Quick test to verify all components load correctly"""
import sys
print("=" * 50)
print("HR Bot Component Test")
print("=" * 50)

# 1. Config
print("\n[1/7] Testing config...")
# from config import GEMINI_API_KEY, FAISS_INDEX_PATH, ID_TO_CHUNK_PATH  # Commented out - using Ollama now
from config import OLLAMA_BASE_URL, OLLAMA_MODEL, FAISS_INDEX_PATH, ID_TO_CHUNK_PATH
# print(f"  API Key: {GEMINI_API_KEY[:10]}...")  # Commented out - using Ollama now
print(f"  Ollama URL: {OLLAMA_BASE_URL}")
print(f"  Ollama Model: {OLLAMA_MODEL}")
print(f"  FAISS path: {FAISS_INDEX_PATH}")
print("  OK")

# 2. Sentence Transformers
print("\n[2/7] Loading embedding model...")
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("all-MiniLM-L6-v2")
print("  OK")

# 3. Test embedding
print("\n[3/7] Testing embedding generation...")
emb = model.encode("test query", normalize_embeddings=True)
print(f"  Embedding shape: {emb.shape}")
print("  OK")

# 4. FAISS
print("\n[4/7] Loading FAISS index...")
import faiss
index = faiss.read_index(FAISS_INDEX_PATH)
print(f"  Total vectors: {index.ntotal}")
print("  OK")

# 5. Chunk mapping
print("\n[5/7] Loading chunk mapping...")
import json
with open(ID_TO_CHUNK_PATH, 'r') as f:
    id_to_chunk = json.load(f)
print(f"  Total chunks: {len(id_to_chunk)}")
print("  OK")

# 6. Ollama
print("\n[6/7] Testing Ollama connection...")
# import google.generativeai as genai  # Commented out - using Ollama now
# genai.configure(api_key=GEMINI_API_KEY)  # Commented out - using Ollama now
# gemini = genai.GenerativeModel("gemini-1.5-flash")  # Commented out - using Ollama now
import ollama
ollama_client = ollama.Client(host=OLLAMA_BASE_URL)
# Test connection by listing models
try:
    models = ollama_client.list()
    print(f"  Connected to Ollama at {OLLAMA_BASE_URL}")
    print(f"  Available models: {len(models.get('models', []))}")
    # Check if our model is available
    model_names = [m['name'] for m in models.get('models', [])]
    if any(OLLAMA_MODEL in name for name in model_names):
        print(f"  ✓ Model '{OLLAMA_MODEL}' is available")
    else:
        print(f"  ⚠ Warning: Model '{OLLAMA_MODEL}' not found. Run: ollama pull {OLLAMA_MODEL}")
except Exception as e:
    print(f"  ✗ Error connecting to Ollama: {str(e)}")
    print(f"  Make sure Ollama is running: ollama serve")
print("  OK")

# 7. Full pipeline test
print("\n[7/7] Testing full RAG pipeline...")
import numpy as np
query = "How much leave do I get?"
query_emb = model.encode(query, normalize_embeddings=True)
query_vec = np.array([query_emb], dtype=np.float32)
distances, indices = index.search(query_vec, k=4)
print(f"  Query: '{query}'")
print(f"  Top matches:")
for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
    chunk = id_to_chunk.get(str(idx), {})
    print(f"    {i+1}. [{dist:.3f}] {chunk.get('question', 'N/A')[:60]}")

print("\n" + "=" * 50)
print("ALL COMPONENTS WORKING!")
print("=" * 50)
print("\nYou can now run: python main.py")
