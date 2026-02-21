"""
Chat Routes - FastAPI endpoints for chat functionality
Handles user questions and returns AI-generated answers
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from app.services.llm_service import generate_answer

router = APIRouter(prefix="/chat", tags=["Chat"])


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    question: str = Field(..., min_length=1, max_length=1000, description="HR-related question")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    answer: str = Field(..., description="AI-generated answer based on HR policies")
    status: str = Field(default="success", description="Response status")


@router.post("/", response_model=ChatResponse, summary="Ask a question")
def chat_endpoint(request: ChatRequest):
    """
    Chat endpoint - Ask HR policy questions

    Returns an answer based on company HR policies using RAG
    """
    try:
        # Generate answer using RAG pipeline
        answer = generate_answer(request.question)

        if not answer:
            raise HTTPException(
                status_code=400,
                detail="Could not generate answer for the given question"
            )

        return ChatResponse(answer=answer, status="success")

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing question: {str(e)}"
        )
