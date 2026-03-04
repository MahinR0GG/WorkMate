from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.memory_service import get_memory_service
from app.services.llm_service import call_llm
from database.sqlite_db import get_history

router = APIRouter(prefix="/memory", tags=["memory"])


# ---------- Request models ----------
class CommitMemoryRequest(BaseModel):
    user_id: str
    session_id: str


class AddMemoryRequest(BaseModel):
    user_id: str
    memory_text: str


# ---------- Helpers ----------
def summarize_session_for_memory(messages: list[dict]) -> str:
    if not messages:
        return ""

    tail = messages[-20:]

    prompt = f"""
You are an HR assistant.

Extract ONLY long-term useful memory from this chat that could help in future conversations.
Include:
- user preferences (if any)
- ongoing tasks / follow-ups
- stable personal/work context the user mentioned
Exclude:
- greetings
- temporary one-off questions

Return 3-7 bullet points.

Chat:
{tail}
""".strip()

    return call_llm(prompt).strip()


# ---------- Endpoints ----------
@router.post("/add")
def add_memory(req: AddMemoryRequest):
    memory_service = get_memory_service()
    memory_id = memory_service.add_memory(req.user_id, req.memory_text)
    return {"status": "ok", "memory_id": memory_id}


@router.get("/search")
def search_memory(user_id: str, query: str, k: int = 2):
    memory_service = get_memory_service()
    results = memory_service.search_memories(user_id=user_id, query=query, k=k)
    return {"status": "ok", "results": results}


@router.post("/commit")
def commit_memory(req: CommitMemoryRequest):

    # FIXED: use get_history
    messages = get_history(req.session_id, limit=50)

    if not messages:
        raise HTTPException(status_code=404, detail="No messages found for this session_id")

    summary = summarize_session_for_memory(messages)

    if not summary:
        raise HTTPException(status_code=400, detail="Summary was empty; nothing to store")

    memory_service = get_memory_service()
    memory_id = memory_service.add_memory(req.user_id, summary)

    return {"status": "ok", "memory_id": memory_id, "summary": summary}