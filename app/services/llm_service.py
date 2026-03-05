"""
LLM Service - Handles RAG pipeline using LangChain for orchestration.
Orchestrates embedding, FAISS search, LangChain STM, and LLM response generation.

Memory architecture:
  - STM (stm_service)   : In-RAM, token-aware, session-scoped — feeds the LLM context window
  - SQLite (sqlite_db)  : Persistent, used for Streamlit UI chat display history
"""

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage

from app.services.llm_factory import get_llm
from app.services.embedding_service import get_embedding
from app.services.vector_service import search_similar_chunks
from app.services.stm_service import add_message, get_trimmed_memory
from database.sqlite_db import save_message


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
    Full RAG + STM pipeline:
    1. Fetch token-trimmed conversation history from LangChain STM
    2. Build a contextualized FAISS query (last assistant turn + new question)
    3. Embed query → search FAISS for relevant HR policy chunks
    4. Build structured prompt (ChatPromptTemplate)
    5. Invoke LangChain chain: prompt | LLM
    6. Store both turns in STM (in-RAM) and SQLite (persistent UI display)
    """
    try:
        # 1. Fetch token-trimmed STM history
        stm_messages = get_trimmed_memory(session_id)

        # Format history as a readable string for the prompt
        history_parts = []
        for msg in stm_messages:
            if isinstance(msg, HumanMessage):
                history_parts.append(f"USER: {msg.content}")
            elif isinstance(msg, AIMessage):
                history_parts.append(f"ASSISTANT: {msg.content}")
        history_text = "\n".join(history_parts) if history_parts else "No previous conversation."

        # 2. Contextualized FAISS query (last assistant reply + new question)
        last_assistant = next(
            (msg.content for msg in reversed(stm_messages) if isinstance(msg, AIMessage)),
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
            # Store in STM and SQLite even for no-result answers
            add_message(session_id, HumanMessage(content=question))
            add_message(session_id, AIMessage(content=answer))
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

        # 6. Persist both turns:
        #    → STM  (token-trimmed in-RAM, for LLM context window)
        add_message(session_id, HumanMessage(content=question))
        add_message(session_id, AIMessage(content=answer))
        #    → SQLite (persistent, for Streamlit UI display)
        save_message(session_id, "user", question)
        save_message(session_id, "assistant", answer)

        return answer

    except Exception as e:
        return f"Error generating response: {str(e)}"
