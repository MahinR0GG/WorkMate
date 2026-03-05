"""
STM Service - Token-aware, session-scoped Short-Term Memory.

Uses LangChain message types and trim_messages (langchain-core >= 0.3).
Token counting is done via tiktoken (cl100k_base BPE) — provider-agnostic,
works for both ChatOllama (llama3) and AzureChatOpenAI (GPT-4o).

Storage: in-RAM dict — intentionally non-persistent.
  - Memory is lost when the server restarts (by design).
  - SQLite in memory_service.py handles persistent display history for the UI.

Public API:
  add_message(session_id, message)      → append a message to the session STM
  get_trimmed_memory(session_id)        → return token-trimmed message list
  clear_session(session_id)             → wipe all messages for a session
"""

from __future__ import annotations

import threading
import tiktoken
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, trim_messages

from app.core.config import MAX_STM_TOKENS

# ── In-RAM store ───────────────────────────────────────────────────────────────
# { session_id: [BaseMessage, ...] }
# Protected by a lock so concurrent FastAPI requests don't corrupt the store.
_store: dict[str, list[BaseMessage]] = {}
_lock  = threading.Lock()

# ── tiktoken encoder (loaded once) ────────────────────────────────────────────
# cl100k_base is the BPE encoding for GPT-3.5/GPT-4.
# It's a good approximation for both Ollama llama3 and Azure OpenAI.
_enc = tiktoken.get_encoding("cl100k_base")


# ── Token counter (used by trim_messages) ─────────────────────────────────────
def _count_tokens(messages: list[BaseMessage]) -> int:
    """
    Count total tokens across all messages.
    Each message gets +4 overhead tokens (role framing), matching OpenAI's
    chat completion format — reasonable approximation for all providers.
    """
    total = 0
    for msg in messages:
        content = msg.content if isinstance(msg.content, str) else str(msg.content)
        total += len(_enc.encode(content)) + 4   # +4 for role/framing overhead
    return total


# ── Public helpers ─────────────────────────────────────────────────────────────

def add_message(session_id: str, message: BaseMessage) -> None:
    """
    Append a LangChain BaseMessage (HumanMessage or AIMessage) to the
    session's STM store.

    Example:
        add_message(session_id, HumanMessage(content="What is sick leave?"))
        add_message(session_id, AIMessage(content="Sick leave is ..."))
    """
    with _lock:
        if session_id not in _store:
            _store[session_id] = []
        _store[session_id].append(message)


def get_trimmed_memory(session_id: str) -> list[BaseMessage]:
    """
    Return the stored messages for a session, trimmed to MAX_STM_TOKENS.

    Trimming strategy:
      - strategy="last"  → oldest messages are dropped first to stay within budget.
      - include_system=False → no system messages stored in the STM.

    Returns an empty list if the session has no history yet.
    """
    with _lock:
        messages = list(_store.get(session_id, []))

    if not messages:
        return []

    trimmed = trim_messages(
        messages,
        max_tokens=MAX_STM_TOKENS,
        token_counter=_count_tokens,
        strategy="last",        # keep most recent messages
        include_system=False,   # system prompt is injected separately in the chain
    )

    return trimmed


def clear_session(session_id: str) -> None:
    """
    Wipe all STM messages for a session.
    Call this when the user clicks 'Clear Chat' or starts a new session.
    """
    with _lock:
        _store.pop(session_id, None)


# ── Diagnostic helper (dev/debug only) ────────────────────────────────────────

def get_session_token_count(session_id: str) -> int:
    """Return the current raw token count for a session (before trimming)."""
    with _lock:
        messages = list(_store.get(session_id, []))
    return _count_tokens(messages) if messages else 0
