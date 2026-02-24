"""
Memory Service - Manages conversation history per session using SQLite.
Thin wrapper around database/sqlite_db.py helpers for use by service layer.
"""

from database.sqlite_db import save_message, get_history


def add_to_memory(session_id: str, role: str, content: str):
    """Save a single message turn to the session memory."""
    save_message(session_id, role, content)


def recall_memory(session_id: str, limit: int = 10) -> list[dict]:
    """Retrieve conversation history for a session (chronological order)."""
    return get_history(session_id, limit=limit)


def clear_memory(session_id: str):
    """
    Clear all messages for a given session.
    Useful for 'New Chat' or reset functionality.
    """
    from database.sqlite_db import get_connection
    conn = get_connection()
    conn.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
