"""
LLM Service - Handles RAG pipeline and Ollama API calls
Orchestrates embedding, search, memory retrieval, and LLM response generation
"""

import ollama
from app.core.config import OLLAMA_BASE_URL, OLLAMA_MODEL
from app.services.embedding_service import get_embedding
from app.services.vector_service import search_similar_chunks
from database.sqlite_db import get_history, save_message

# Configure Ollama client
ollama_client = ollama.Client(host=OLLAMA_BASE_URL)


def generate_answer(question: str, session_id: str) -> str:
    """
    Full RAG + memory pipeline:
    1. Fetch recent conversation history from SQLite
    2. Convert question to embedding
    3. Search FAISS for relevant HR policy chunks
    4. Build a prompt that includes history + RAG context
    5. Call Ollama LLM
    6. Save both turns (user + assistant) to SQLite
    """
    try:
        # 1. Fetch conversation history for this session
        history = get_history(session_id, limit=10)

        # Format history as a readable string for the prompt
        if history:
            history_text = "\n".join(
                f"{msg['role'].upper()}: {msg['content']}" for msg in history
            )
        else:
            history_text = "No previous conversation."

        # 2. Build a contextualized search query for FAISS.
        # Follow-up questions like "Can I carry them forward?" have no HR keywords
        # on their own. Prepending the last assistant reply gives the embedding
        # model the topic context it needs to find relevant policy chunks.
        last_assistant = next(
            (msg["content"] for msg in reversed(history) if msg["role"] == "assistant"),
            None
        )
        if last_assistant:
            faiss_query = f"{last_assistant}\n{question}"
        else:
            faiss_query = question

        # 3. Embed the contextualized query and search FAISS
        query_embedding = get_embedding(faiss_query)
        relevant_chunks = search_similar_chunks(query_embedding)

        # Handle no results
        if not relevant_chunks:
            answer = "I couldn't find relevant HR policy information for your question. Please contact HR for assistance."
            save_message(session_id, "user", question)
            save_message(session_id, "assistant", answer)
            return answer

        # 4. Build context from RAG chunks
        rag_context = "\n\n".join([
            f"Q: {chunk['question']}\nA: {chunk['answer']}"
            for chunk in relevant_chunks
        ])

        # 5. Build full prompt with history + RAG context
        prompt = f"""You are a professional HR assistant. Use ONLY the provided policy context to answer the employee's question.

CONVERSATION HISTORY:
{history_text}

POLICY CONTEXT:
{rag_context}

EMPLOYEE QUESTION:
{question}

RESPONSE RULES:
- Answer clearly and concisely.
- Use bullet points if listing items.
- Do NOT include phrases like "Based on the provided context".
- Do NOT add assumptions or external knowledge.
- If the answer is not found in the context, say:
  "The requested information is not available in the current HR policy documents."
- Keep the tone professional and direct."""

        # 6. Call Ollama
        answer = call_llm(prompt)

        # 7. Save both turns to SQLite memory
        save_message(session_id, "user", question)
        save_message(session_id, "assistant", answer)

        return answer

    except Exception as e:
        return f"Error generating response: {str(e)}"


def call_llm(prompt: str) -> str:
    """
    Direct LLM call to Ollama.

    Args:
        prompt: The complete prompt to send to Ollama

    Returns:
        Generated response text
    """
    try:
        response = ollama_client.chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ]
        )
        return response['message']['content']
    except Exception as e:
        print(f"Error calling Ollama API: {str(e)}")
        raise
