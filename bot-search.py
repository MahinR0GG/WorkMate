import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

from config import (
    GEMINI_API_KEY,
    FAISS_INDEX_PATH,
    ID_TO_CHUNK_PATH,
    EMBEDDING_MODEL,
    TOP_K,
    SIMILARITY_THRESHOLD
)

# =========================
# SANITY CHECKS
# =========================
assert os.path.exists(FAISS_INDEX_PATH), "FAISS index file not found"
assert os.path.exists(ID_TO_CHUNK_PATH), "id_to_chunk.json not found"

# =========================
# LOAD MODELS
# =========================
print("Loading embedding model...")
embedder = SentenceTransformer(EMBEDDING_MODEL)

print("Loading FAISS index...")
faiss_index = faiss.read_index(FAISS_INDEX_PATH)

print("Loading chunk mappings...")
with open(ID_TO_CHUNK_PATH, "r", encoding="utf-8") as f:
    id_to_chunk = json.load(f)

print(f"Loaded {len(id_to_chunk)} chunks")

# =========================
# GEMINI SETUP
# =========================
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

# =========================
# EMBED QUERY
# =========================
def embed_query(query: str):
    embedding = embedder.encode(
        [query],
        normalize_embeddings=True
    )
    return np.array(embedding).astype("float32")

# =========================
# RETRIEVE CHUNKS
# =========================
def retrieve_chunks(query: str):
    query_embedding = embed_query(query)

    # FAISS search returns similarity scores (inner product) for IndexFlatIP
    # Higher scores = more similar (range: -1 to 1 for normalized embeddings)
    similarities, indices = faiss_index.search(query_embedding, TOP_K)

    # Debug: Print raw FAISS scores for verification
    print(f"\n[DEBUG] Raw FAISS scores: {similarities[0]}")
    print(f"[DEBUG] Similarity threshold: {SIMILARITY_THRESHOLD}")

    results = []
    for similarity, idx in zip(similarities[0], indices[0]):
        if idx == -1:
            continue

        # For IndexFlatIP: higher similarity is better, so use >= threshold
        if similarity >= SIMILARITY_THRESHOLD:
            chunk = id_to_chunk.get(str(idx))
            if not chunk:
                continue

            context_text = (
                f"Question: {chunk.get('question', '')}\n"
                f"Answer: {chunk.get('answer', '')}"
            )

            results.append({
                "text": context_text,
                "metadata": {
                    "doc_name": chunk.get("doc_name"),
                    "chunk_id": chunk.get("chunk_id")
                },
                "similarity": float(similarity)  # Renamed from 'distance'
            })

    print(f"[DEBUG] Retrieved {len(results)} chunks above threshold\n")
    return results

# =========================
# BUILD PROMPT
# =========================
def build_prompt(context_chunks, question):
    if not context_chunks:
        return None

    context_text = "\n\n".join(
        f"- {chunk['text']}" for chunk in context_chunks
    )

    prompt = f"""
You are an HR assistant chatbot.

Answer the user's question using ONLY the information provided in the context.
Do NOT use external knowledge.
If the answer is not present, say:
"Information not available in the HR policy."

Context:
{context_text}

Question:
{question}

Answer:
""".strip()

    return prompt

# =========================
# GENERATE ANSWER
# =========================
def generate_answer(prompt):
    response = gemini_model.generate_content(prompt)
    return response.text.strip()

# =========================
# MAIN BOT FUNCTION
# =========================
def ask_hr_bot(question: str):
    retrieved_chunks = retrieve_chunks(question)

    if not retrieved_chunks:
        return "Information not available in the HR policy."

    prompt = build_prompt(retrieved_chunks, question)
    if not prompt:
        return "Information not available in the HR policy."

    return generate_answer(prompt)

# =========================
# CLI MODE
# =========================
if __name__ == "__main__":
    print("\nHR Bot is ready 🤖 (type 'exit' to quit)\n")

    while True:
        user_question = input("You: ")
        if user_question.lower() == "exit":
            break

        answer = ask_hr_bot(user_question)
        print(f"\nHR Bot: {answer}\n")
