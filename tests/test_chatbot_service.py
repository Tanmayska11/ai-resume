# tests/test_chatbot_service.py

import os
import pytest

from chatbot.service import ResumeChatbotService




@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set",
)
def test_chatbot_returns_answer(monkeypatch):
        from chatbot.service import ResumeChatbotService

        # Fake OpenAI response
        def fake_generate_answer(self, *, context, question):
            return "I have experience building data pipelines and analytics systems."

        # Replace real OpenAI call with fake one
        monkeypatch.setattr(
            "chatbot.llm.client.LLMClient.generate_answer",
            fake_generate_answer,
        )

        bot = ResumeChatbotService()
        answer = bot.answer("What data engineering experience do you have?")

        assert isinstance(answer, str)
        assert "data" in answer.lower()



def test_empty_question():
    bot = ResumeChatbotService()
    answer = bot.answer("")
    assert "ask a question" in answer.lower()


def test_missing_context_refusal(monkeypatch):
    from chatbot.llm.client import LLMClient

    def fake_context(*args, **kwargs):
        return ""

    monkeypatch.setattr(
        "chatbot.service.retrieve_context",
        fake_context,
    )

    bot = ResumeChatbotService()
    answer = bot.answer("What is your Kubernetes experience?")
    assert "not mentioned" in answer.lower()
