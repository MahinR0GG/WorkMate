import sqlite3
from typing import List, Dict, Optional

class SQLiteMemoryStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()

    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id TEXT PRIMARY KEY,
                summary TEXT DEFAULT '',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """)
            cur.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                route_used TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(conversation_id) REFERENCES conversations(conversation_id)
            )
            """)
            con.commit()

    def ensure_conversation(self, conversation_id: str):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("INSERT OR IGNORE INTO conversations (conversation_id) VALUES (?)", (conversation_id,))
            con.commit()

    def add_message(self, conversation_id: str, role: str, content: str, route_used: Optional[str] = None):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute(
                "INSERT INTO messages (conversation_id, role, content, route_used) VALUES (?, ?, ?, ?)",
                (conversation_id, role, content, route_used),
            )
            con.commit()

    def get_recent_messages(self, conversation_id: str, limit: int) -> List[Dict]:
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("""
                SELECT role, content, route_used, created_at
                FROM messages
                WHERE conversation_id=?
                ORDER BY id DESC
                LIMIT ?
            """, (conversation_id, limit))
            rows = cur.fetchall()
        # return oldest->newest
        rows.reverse()
        return [{"role": r[0], "content": r[1], "route_used": r[2], "created_at": r[3]} for r in rows]

    def get_summary(self, conversation_id: str) -> str:
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("SELECT summary FROM conversations WHERE conversation_id=?", (conversation_id,))
            row = cur.fetchone()
        return row[0] if row else ""

    def set_summary(self, conversation_id: str, summary: str):
        with self._conn() as con:
            cur = con.cursor()
            cur.execute("UPDATE conversations SET summary=? WHERE conversation_id=?", (summary, conversation_id))
            con.commit()
