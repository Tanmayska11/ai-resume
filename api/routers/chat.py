from fastapi import APIRouter, HTTPException
from api.schemas.chat import ChatRequest, ChatResponse
from chatbot.service import ResumeChatbotService


router = APIRouter(prefix="/chat", tags=["chat"])

# SINGLE instance (important)
def get_chatbot():
    global chatbot
    if chatbot is None:
        chatbot = ResumeChatbotService()
    return chatbot


@router.post("/ask", response_model=ChatResponse)
def ask_chatbot(payload: ChatRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question is empty")

    result = get_chatbot().answer(payload.question)

    return {
        "answer": result["answer"],
        "sources": result.get("sources", []),
    }
