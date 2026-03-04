import os
import json
import sqlite3
from datetime import datetime
from typing import Callable, Dict, List, Optional

import numpy as np
import faiss
print("🔥 LOADED MEMORY_SERVICE FROM:", __file__)

class MemoryService:
    """
    Long-Term Memory service:
    - stores memory text in SQLite table `memories`
    - stores embeddings in FAISS index (persistent on disk)
    - maintains a meta json mapping FAISS row -> SQLite memory_id
    """

    def __init__(
        self,
        db_path: str,
        embed_fn: Callable[[str], np.ndarray],
        dim: int,
        index_path: str = "vector_index/memory_index.faiss",
        meta_path: str = "vector_index/memory_meta.json",
    ):
        self.db_path = db_path
        self.embed_fn = embed_fn
        self.dim = dim
        self.index_path = index_path
        self.meta_path = meta_path

        # Ensure folders exist (safe even if paths change)
        idx_dir = os.path.dirname(self.index_path)
        if idx_dir:
            os.makedirs(idx_dir, exist_ok=True)

        meta_dir = os.path.dirname(self.meta_path)
        if meta_dir:
            os.makedirs(meta_dir, exist_ok=True)

        # Ensure DB table exists (GUARANTEED fix for "no such table: memories")
        self._ensure_memories_table()

        # Load/create index + meta
        self.index = self._load_or_create_index()
        self.meta = self._load_or_create_meta()

        # Safety: meta size should match FAISS count (can drift if files got corrupted)
        if self.index.ntotal != len(self.meta.get("ids", [])):
            # Re-sync to the smaller of the two to avoid index errors
            min_len = min(self.index.ntotal, len(self.meta.get("ids", [])))
            if min_len == 0:
                # reset everything cleanly
                self._reset_index_and_meta()
            else:
                # trim meta
                self.meta["ids"] = self.meta["ids"][:min_len]
                self._save_meta()

    # -------------------- DB helpers --------------------
    def _conn(self):
        return sqlite3.connect(self.db_path)

    def _ensure_memories_table(self):
        conn = self._conn()
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT NOT NULL,
            memory_text TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """)
        conn.commit()
        conn.close()

    # -------------------- FAISS + meta persistence --------------------
    def _reset_index_and_meta(self):
        # delete old files if present
        try:
            if os.path.exists(self.index_path):
                os.remove(self.index_path)
        except OSError:
            pass

        try:
            if os.path.exists(self.meta_path):
                os.remove(self.meta_path)
        except OSError:
            pass

        # recreate fresh
        self.index = faiss.IndexFlatIP(self.dim)
        faiss.write_index(self.index, self.index_path)
        self.meta = {"ids": []}
        self._save_meta()

    def _load_or_create_index(self):
        """
        Loads FAISS index if valid.
        If corrupted/empty, auto-deletes and recreates.
        """
        if os.path.exists(self.index_path):
            try:
                return faiss.read_index(self.index_path)
            except Exception:
                # corrupted index -> delete and recreate
                try:
                    os.remove(self.index_path)
                except OSError:
                    pass
                # meta likely mismatched too
                try:
                    if os.path.exists(self.meta_path):
                        os.remove(self.meta_path)
                except OSError:
                    pass

        index = faiss.IndexFlatIP(self.dim)
        faiss.write_index(index, self.index_path)
        return index

    def _load_or_create_meta(self) -> Dict[str, List[int]]:
        if os.path.exists(self.meta_path):
            try:
                with open(self.meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                if isinstance(meta, dict) and "ids" in meta and isinstance(meta["ids"], list):
                    return meta
            except Exception:
                pass

        meta = {"ids": []}
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        return meta

    def _save_index(self):
        faiss.write_index(self.index, self.index_path)

    def _save_meta(self):
        with open(self.meta_path, "w", encoding="utf-8") as f:
            json.dump(self.meta, f, indent=2)

    # -------------------- Public API --------------------
    def add_memory(self, user_id: str, memory_text: str) -> int:
        """
        1) Insert into SQLite -> memory_id
        2) Embed memory_text -> vector
        3) Add to FAISS
        4) Append memory_id into meta
        5) Persist index + meta to disk
        """
        created_at = datetime.utcnow().isoformat()

        # Insert into SQLite
        conn = self._conn()
        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO memories (user_id, memory_text, created_at) VALUES (?, ?, ?)",
                (user_id, memory_text, created_at),
            )
            conn.commit()
            memory_id = cur.lastrowid
        finally:
            conn.close()

        # Embed
        vec = self.embed_fn(memory_text)
        vec = np.asarray(vec, dtype=np.float32)

        if vec.ndim != 1 or vec.shape[0] != self.dim:
            raise ValueError(f"Embedding shape mismatch. Expected ({self.dim},) got {vec.shape}")

        # Normalize for cosine similarity with IndexFlatIP
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm

        # Add to index
        self.index.add(vec.reshape(1, -1))

        # Meta maps index row -> memory_id
        self.meta["ids"].append(int(memory_id))

        # Persist
        self._save_index()
        self._save_meta()

        return int(memory_id)

    def search_memories(self, user_id: str, query: str, k: int = 2) -> List[Dict]:
        """
        Search FAISS for top-k memories.
        Filters results by user_id (SQLite fetch).
        """
        if self.index.ntotal == 0:
            return []

        qv = self.embed_fn(query)
        qv = np.asarray(qv, dtype=np.float32)

        if qv.ndim != 1 or qv.shape[0] != self.dim:
            raise ValueError(f"Query embedding shape mismatch. Expected ({self.dim},) got {qv.shape}")

        # Normalize for cosine similarity
        norm = np.linalg.norm(qv)
        if norm > 0:
            qv = qv / norm

        scores, idxs = self.index.search(qv.reshape(1, -1), k)

        results: List[Dict] = []
        conn = self._conn()
        try:
            cur = conn.cursor()

            for score, idx in zip(scores[0], idxs[0]):
                if idx < 0:
                    continue
                if idx >= len(self.meta["ids"]):
                    continue

                memory_id = self.meta["ids"][idx]

                cur.execute(
                    "SELECT id, user_id, memory_text, created_at FROM memories WHERE id = ? AND user_id = ?",
                    (memory_id, user_id),
                )
                row = cur.fetchone()
                if row:
                    results.append(
                        {
                            "id": row[0],
                            "user_id": row[1],
                            "text": row[2],
                            "created_at": row[3],
                            "score": float(score),
                        }
                    )
        finally:
            conn.close()

        return results


# -------------------- Singleton accessor --------------------
_memory_service: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """
    Lazy singleton initialization so you don't recreate the FAISS index per request.
    """
    global _memory_service

    if _memory_service is None:
        # IMPORTANT: adjust these imports ONLY if your paths differ
        from app.services.embedding_service import get_embedding, model as embedding_model
        from database.sqlite_db import DB_PATH

        def _embed_fn(text: str) -> np.ndarray:
            return np.asarray(get_embedding(text), dtype=np.float32)

        # Determine embedding dimension safely
        if hasattr(embedding_model, "get_sentence_embedding_dimension"):
            dim = int(embedding_model.get_sentence_embedding_dimension())
        else:
            dim = int(_embed_fn("test").shape[0])

        _memory_service = MemoryService(
            db_path=DB_PATH,
            embed_fn=_embed_fn,
            dim=dim,
            index_path="vector_index/memory_index.faiss",
            meta_path="vector_index/memory_meta.json",
        )

    return _memory_service