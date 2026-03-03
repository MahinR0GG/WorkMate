"""
LLM Service - Handles RAG pipeline using LangChain for orchestration.
Orchestrates embedding, FAISS search, SQLite memory, and LLM response generation.
"""

from langchain_core.prompts import ChatPromptTemplate
from app.services.llm_factory import get_llm
from app.services.embedding_service import get_embedding
from app.services.vector_service import search_similar_chunks
from database.sqlite_db import get_history, save_message


# ── System prompt ──────────────────────────────────────────────────────────────
_SYSTEM_PROMPT = """You are a professional HR assistant. \
Use ONLY the provided policy context to answer the employee's question.

RESPONSE RULES:
- Answer clearly and concisely.
- Use bullet points if listing items.
- Do NOT include phrases like "Based on the provided context".
- Do NOT add assumptions or external knowledge.
- If the answer is not found in the context, say: \
  "The requested information is not available in the current HR policy documents."
- Keep the tone professional and direct."""

# ── Prompt template ────────────────────────────────────────────────────────────
_prompt = ChatPromptTemplate.from_messages([
    ("system", _SYSTEM_PROMPT),
    ("human",
     "CONVERSATION HISTORY:\n{history}\n\n"
     "POLICY CONTEXT:\n{context}\n\n"
     "EMPLOYEE QUESTION:\n{question}"),
])


def generate_answer(question: str, session_id: str) -> str:
    """
    Full RAG + memory pipeline (LangChain orchestrated):
    1. Fetch recent conversation history from SQLite
    2. Build a contextualized FAISS query (last assistant turn + new question)
    3. Embed query → search FAISS for relevant HR policy chunks
    4. Build structured prompt (ChatPromptTemplate)
    5. Invoke LangChain chain: prompt | LLM
    6. Save both turns (user + assistant) to SQLite
    """
    try:
        # 1. Fetch conversation history
        history = get_history(session_id, limit=10)

        history_text = (
            "\n".join(f"{msg['role'].upper()}: {msg['content']}" for msg in history)
            if history else "No previous conversation."
        )

        # 2. Contextualized FAISS query (blend last assistant reply + new question)
        last_assistant = next(
            (msg["content"] for msg in reversed(history) if msg["role"] == "assistant"),
            None,
        )
        faiss_query = f"{last_assistant}\n{question}" if last_assistant else question

        # 3. Embed + search FAISS
        query_embedding = get_embedding(faiss_query)
        relevant_chunks = search_similar_chunks(query_embedding)

        if not relevant_chunks:
            answer = (
                "I couldn't find relevant HR policy information for your question. "
                "Please contact HR for assistance."
            )
            save_message(session_id, "user", question)
            save_message(session_id, "assistant", answer)
            return answer

        # 4. Build RAG context string
        rag_context = "\n\n".join(
            f"Q: {chunk['question']}\nA: {chunk['answer']}"
            for chunk in relevant_chunks
        )

        # 5. Build and invoke LangChain chain  (prompt | llm)
        chain = _prompt | get_llm()
        response = chain.invoke({
            "history": history_text,
            "context": rag_context,
            "question": question,
        })

        # response is an AIMessage — extract text via .content
        answer = response.content

        # 6. Persist both turns
        save_message(session_id, "user", question)
        save_message(session_id, "assistant", answer)

        return answer

    except Exception as e:
        return f"Error generating response: {str(e)}"
