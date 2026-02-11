import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List


# -----------------------------
# Config
# -----------------------------
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"
FAISS_INDEX_PATH = "embeddings/faiss_index.bin"
ID_TO_CHUNK_PATH = "embeddings/id_to_chunk.json"
TOP_K = 3


# -----------------------------
# Load resources
# -----------------------------
def load_faiss_index(path: str) -> faiss.Index:
    index = faiss.read_index(path)
    return index


def load_id_to_chunk(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


# -----------------------------
# Embed query
# -----------------------------
def embed_query(model, query: str) -> np.ndarray:
    embedding = model.encode(query, convert_to_numpy=True)
    return embedding.reshape(1, -1).astype("float32")


# -----------------------------
# Search FAISS
# -----------------------------
def search_faiss(
    index: faiss.Index,
    query_embedding: np.ndarray,
    top_k: int
) -> List[int]:
    distances, indices = index.search(query_embedding, top_k)
    return indices[0], distances[0]


# -----------------------------
# Main retrieval logic
# -----------------------------
def retrieve_answers(question: str):
    # Load everything
    model = load_embedding_model()
    index = load_faiss_index(FAISS_INDEX_PATH)
    id_to_chunk = load_id_to_chunk(ID_TO_CHUNK_PATH)

    # Embed question
    query_embedding = embed_query(model, question)

    # Search
    retrieved_ids, distances = search_faiss(index, query_embedding, TOP_K)

    results = []

    for idx, dist in zip(retrieved_ids, distances):
        chunk = id_to_chunk.get(str(idx))
        if not chunk:
            continue

        results.append({
            "distance": float(dist),
            "doc_name": chunk.get("doc_name"),
            "chunk_id": chunk.get("chunk_id"),
            "question": chunk.get("question"),
            "answer": chunk.get("answer")
        })

    return results


# -----------------------------
# CLI usage
# -----------------------------
if __name__ == "__main__":
    print("\nHR_BOT — Semantic Search\n")
    user_question = input("Ask a question: ").strip()

    answers = retrieve_answers(user_question)

    if not answers:
        print("\n❌ No relevant answer found.")
    else:
        print("\n✅ Top Matches:\n")
        for i, ans in enumerate(answers, 1):
            print(f"{i}. Answer:")
            print(ans["answer"])
            print(
                f"   Source: {ans['doc_name']} "
                f"(chunk_id: {ans['chunk_id']})"
            )
            print(f"   Distance: {ans['distance']:.4f}\n")
