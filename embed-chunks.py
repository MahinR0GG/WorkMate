import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# CONFIG
CHUNKS_DIR = r"C:\Mahin\HR-Bot\chunks+metadata"
OUTPUT_DIR = r"C:\Mahin\HR-Bot\embeddings"

MODEL_NAME = "all-MiniLM-L6-v2"

# SETUP
os.makedirs(OUTPUT_DIR, exist_ok=True)

model = SentenceTransformer(MODEL_NAME)

texts = []
id_to_chunk = {}

# LOAD CHUNKS
idx = 0
for file_name in os.listdir(CHUNKS_DIR):
    if not file_name.endswith(".json"):
        continue

    file_path = os.path.join(CHUNKS_DIR, file_name)

    with open(file_path, "r", encoding="utf-8") as f:
        chunk = json.load(f)

    combined_text = f"Question: {chunk['question']}\nAnswer: {chunk['answer']}"
    texts.append(combined_text)

    id_to_chunk[idx] = chunk
    idx += 1

print(f"Loaded {len(texts)} chunks")

# CREATE EMBEDDINGS (NORMALIZED)
embeddings = model.encode(texts, convert_to_numpy=True, normalize_embeddings=True)

dimension = embeddings.shape[1]
print(f"Embedding dimension: {dimension}")

# BUILD FAISS INDEX (Inner Product for cosine similarity with normalized embeddings)
index = faiss.IndexFlatIP(dimension)
index.add(embeddings)

print("FAISS index created")

# SAVE TO DISK
faiss.write_index(index, os.path.join(OUTPUT_DIR, "faiss_index.bin"))

with open(os.path.join(OUTPUT_DIR, "id_to_chunk.json"), "w", encoding="utf-8") as f:
    json.dump(id_to_chunk, f, indent=2)

print("Embeddings and metadata saved successfully")
