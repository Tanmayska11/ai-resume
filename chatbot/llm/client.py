# chatbot/llm/client.py

"""
LLM client for resume chatbot.

Responsibilities:
- Call the LLM with grounded context
- Enforce strict system + user prompting
- Fail safely when context or configuration is missing
"""

import os
from openai import OpenAI

from chatbot.llm.prompt_templates import (
    SYSTEM_PROMPT,
    USER_PROMPT_TEMPLATE,
)

# Fast, cost-effective, RAG-friendly model
MODEL_NAME = "gpt-4o-mini"


class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("OPENAI_API_KEY environment variable is not set")

        # OpenAI Python SDK (new style)
        self.client = OpenAI(api_key=api_key)

    def generate_answer(self, *, context: str, question: str) -> str:
        """
        Generate a grounded answer from retrieved context.

        If the answer is not present in context, the model is instructed
        to explicitly say so (via SYSTEM_PROMPT).
        """

        if not context or not context.strip():
            return "That information is not mentioned in my resume or GitHub projects."

        prompt = USER_PROMPT_TEMPLATE.format(
            context=context,
            question=question,
        )

        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,  # low = factual, grounded
                max_tokens=400,
            )
        except Exception as e:
            # Fail gracefully — never crash UI
            return (
                "I encountered an issue while generating the answer. "
                "Please try again."
            )

        content = response.choices[0].message.content
        return content.strip() if content else (
            "That information is not mentioned in my resume or GitHub projects."
        )
