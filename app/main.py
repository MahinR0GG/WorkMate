"""
HR Bot API - Main application entry point
RAG-based HR assistant for answering policy questions
"""

from fastapi import FastAPI
from app.routes import chat
import uvicorn

app = FastAPI(
    title="HR Bot API",
    description="AI HR Assistant powered by RAG (Retrieval-Augmented Generation)",
    version="1.0.0"
)

# Include routers
app.include_router(chat.router)

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
