import time
from typing import List, Dict, Optional
from dataclasses import dataclass

# ✅ Reuse your existing SQLite functions (CHANGE IMPORT PATHS)
# These MUST already exist in your project (same ones used in generate_answer).
from database.sqlite_db import get_history, save_message  # <- update path if different


@dataclass
class CacheItem:
    messages: List[Dict[str, str]]
    last_access: float


class SessionStore:
    """
    STM as cache + SQLite as source of truth.

    - Cache holds recent messages for fast access (temporary).
    - SQLite holds full persistent log (optional: still save every turn).
    """

    def __init__(self, ttl_seconds: int = 3600, max_messages: int = 20):
        self.ttl_seconds = ttl_seconds
        self.max_messages = max_messages
        self._cache: Dict[str, CacheItem] = {}

    # ---------- Cache helpers ----------
    def _now(self) -> float:
        return time.time()

    def _is_expired(self, item: CacheItem) -> bool:
        return (self._now() - item.last_access) > self.ttl_seconds

    def _trim(self, msgs: List[Dict[str, str]]) -> List[Dict[str, str]]:
        if len(msgs) <= self.max_messages:
            return msgs
        return msgs[-self.max_messages :]

    def _touch(self, session_id: str):
        if session_id in self._cache:
            self._cache[session_id].last_access = self._now()

    def cleanup(self):
        """Remove expired sessions from in-memory cache."""
        expired = [sid for sid, item in self._cache.items() if self._is_expired(item)]
        for sid in expired:
            del self._cache[sid]

    # ---------- Public API ----------
    def get_recent_messages(self, session_id: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Return recent messages for session.
        1) Try cache
        2) Fallback to SQLite
        """
        self.cleanup()

        item = self._cache.get(session_id)
        if item and not self._is_expired(item):
            item.last_access = self._now()
            return item.messages[-limit:]

        # fallback to DB
        db_msgs = get_history(session_id, limit=max(limit, self.max_messages))

        # ensure dict format [{"role": "...", "content": "..."}]
        # If your get_history already returns this, this loop does nothing harmful.
        normalized = [{"role": m["role"], "content": m["content"]} for m in db_msgs] if db_msgs else []

        # warm cache
        self._cache[session_id] = CacheItem(messages=self._trim(normalized), last_access=self._now())
        return normalized[-limit:]

    def append_message(self, session_id: str, role: str, content: str, persist: bool = True):
        """
        Append a message to cache, and optionally persist to SQLite.
        """
        self.cleanup()

        msg = {"role": role, "content": content}

        # update cache
        item = self._cache.get(session_id)
        if item and not self._is_expired(item):
            item.messages.append(msg)
            item.messages = self._trim(item.messages)
            item.last_access = self._now()
        else:
            self._cache[session_id] = CacheItem(messages=self._trim([msg]), last_access=self._now())

        # persist to DB (recommended so you never lose history)
        if persist:
            save_message(session_id, role, content)

    def clear_session(self, session_id: str):
        """Clear cache for a session (does NOT delete SQLite history)."""
        if session_id in self._cache:
            del self._cache[session_id]


# Singleton accessor (simple)
_store: Optional[SessionStore] = None

def get_session_store() -> SessionStore:
    global _store
    if _store is None:
        # choose sensible defaults
        _store = SessionStore(ttl_seconds=3600, max_messages=20)  # 1 hour, last 20 msgs
    return _store