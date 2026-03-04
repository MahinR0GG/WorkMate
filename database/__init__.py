"""
Database package initializer.

Provides easy access to SQLite helper functions.
"""

from .sqlite_db import get_history, save_message, init_db, get_connection

__all__ = [
    "get_history",
    "save_message",
    "init_db",
    "get_connection",
]
