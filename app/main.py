"""
HR Bot API - Main application entry point
RAG-based HR assistant for answering policy questions

Note: importing `app` requires the project root to be on Python's search
path. When you execute this file directly (`python app/main.py`), Python
adds the `app/` directory itself to `sys.path`, causing `import app.routes`
to fail with ``ModuleNotFoundError``. The recommended ways to run the server
are shown in README.md.
"""

# ensure project root is on sys.path so `import app...` works even when
# running the script directly (helpful for quick tests).
import os
import sys
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from fastapi import FastAPI
from app.routes import chat
from app.routes import memory
from database.sqlite_db import init_db
import uvicorn



app = FastAPI(
    title="HR Bot API",
    description="AI HR Assistant powered by RAG (Retrieval-Augmented Generation)",
    version="1.0.0",
    debug=True
)

# Include routers
app.include_router(chat.router)
app.include_router(memory.router)

@app.on_event("startup")
def startup_event():
    """Initialize the SQLite database on server startup."""
    print("FastAPI is starting...")
    init_db()

@app.get("/")
def read_root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "HR Bot API is running",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check for monitoring"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )
