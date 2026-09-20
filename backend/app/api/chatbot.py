"""POST /api/chat – Rule-based sustainability assistant."""

from fastapi import APIRouter
from app.schemas.pollution_event import ChatRequest, ChatResponse
from app.services.explanation import chatbot_response

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Answer air-quality and sustainability questions using a rule-based engine."""
    answer = chatbot_response(request.question)
    return ChatResponse(answer=answer)
