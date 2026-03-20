from fastapi import APIRouter, HTTPException
from api.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


# 🔥 lazy singleton
_chatbot_instance = None


def get_chatbot():
    global _chatbot_instance

    if _chatbot_instance is None:
        from chatbot.service import ResumeChatbotService  # lazy import
        _chatbot_instance = ResumeChatbotService()

    return _chatbot_instance


@router.post("/ask", response_model=ChatResponse)
def ask_chatbot(payload: ChatRequest):
    if not payload.question.strip():
        raise HTTPException(status_code=400, detail="Question is empty")

    chatbot = get_chatbot()

    result = chatbot.answer(payload.question)

    return {
        "answer": result["answer"],
        "sources": result.get("sources", []),
    }