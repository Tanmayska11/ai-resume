import os
from chatbot.runtime_config import config


class ResumeChatbotService:
    """
    Orchestrates retrieval + answer generation for the resume chatbot.
    """

    _instance_retriever = None

    def __init__(self):
        self._retriever = None
        self._llm = None

    # ----------------------------
    # Lazy-loaded retriever
    # ----------------------------
    @property
    def retriever(self):
        if ResumeChatbotService._instance_retriever is None:
            # 🔥 lazy import
            from chatbot.retrieval.retriever import ResumeRetriever

            ResumeChatbotService._instance_retriever = ResumeRetriever()

        return ResumeChatbotService._instance_retriever

    # ----------------------------
    # Lazy-loaded LLM
    # ----------------------------
    def _get_llm(self):
        if self._llm is None:
            # 🔥 lazy import
            from chatbot.llm.client import LLMClient

            self._llm = LLMClient()

        return self._llm

    # ----------------------------
    # Cache invalidation
    # ----------------------------
    @classmethod
    def invalidate(cls):
        cls._instance_retriever = None

    # ----------------------------
    # Public API
    # ----------------------------
    def answer(self, question: str) -> dict:
        if not question or not question.strip():
            return {
                "answer": "Please ask a question about my experience, projects, or skills.",
            }

        results = self.retriever.retrieve(question)

        if not results:
            return {
                "answer": "That information is not mentioned in my resume or projects.",
            }

        mode = config.llm_mode

        # ===========================
        # MOCK MODE
        # ===========================
        if mode == "mock":
            answer_text = self._format_answer(results)

        # ===========================
        # LIVE MODE
        # ===========================
        else:
            llm = self._get_llm()

            context = "\n\n".join(r["text"] for r in results)

            answer_text = llm.generate_answer(
                context=context,
                question=question,
            )

        return {
            "answer": answer_text,
        }

    # =====================================================
    # FORMATTERS (UNCHANGED LOGIC)
    # =====================================================

    def _format_answer(self, results: list[dict]) -> str:

        if all(r.get("section") == "extracurricular_activities" for r in results):
            return self._format_extracurriculars(results)

        if all(r.get("section") == "languages" for r in results):
            return self._format_languages(results)

        if all(r.get("section") == "skills" for r in results):
            return self._format_skills(results)

        if any(
            r.get("role_id") or
            r.get("project_id") or
            r.get("education_id") or
            r.get("certification_id")
            for r in results
        ):
            return self._format_grouped(results)

        return self._format_simple(results)

    def _format_simple(self, results: list[dict]) -> str:
        seen = set()
        bullets = []

        for r in results:
            text = r["text"].strip()
            if not text or text in seen:
                continue
            seen.add(text)

            if ":" in text:
                label, value = text.split(":", 1)
                bullets.append(f"- **{label.strip()}:** {value.strip()}")
            else:
                bullets.append(f"- {text}")

        return "\n".join(bullets)

    def _format_skills(self, results: list[dict]) -> str:
        from collections import defaultdict

        grouped = defaultdict(list)

        for r in results:
            category = r.get("category", "Other")
            skill = r["text"]

            if skill not in grouped[category]:
                grouped[category].append(skill)

        blocks = []

        for category, skills in grouped.items():
            blocks.append(f"- **{category}**")
            for skill in skills:
                blocks.append(f"  - {skill}")
            blocks.append("")

        return "\n".join(blocks).strip()

    def _format_languages(self, results: list[dict]) -> str:
        seen = set()
        lines = []

        for r in results:
            text = r["text"]
            if text in seen:
                continue
            seen.add(text)

            language, proficiency = text.split(":", 1)
            lines.append(f"- **{language.strip()}:** {proficiency.strip()}")

        return "\n".join(lines)

    def _format_extracurriculars(self, results: list[dict]) -> str:
        seen = set()
        lines = []

        for r in results:
            text = r["text"]
            if text in seen:
                continue
            seen.add(text)
            lines.append(f"- {text}")

        return "\n".join(lines)

    def _format_grouped(self, results: list[dict]) -> str:
        groups = {}

        for r in results:
            group_key = (
                r.get("role_id")
                or r.get("project_id")
                or r.get("education_id")
                or r.get("certification_id")
            )
            groups.setdefault(group_key, []).append(r)

        blocks = []

        for items in groups.values():
            section = items[0].get("section")

            header = duration = location = context = None
            responsibilities = []
            learning_outcomes = []
            description = scope = role = None
            outcomes = []
            links = []
            tools = []
            courses = []
            issuer = None
            credentials = []

            for r in items:
                field = r.get("field")
                text = r["text"]

                if field == "header":
                    header = text
                elif field == "duration":
                    duration = text
                elif field == "location":
                    location = text
                elif field == "context":
                    context = text
                elif field == "description":
                    description = text.replace("Description:", "").strip()
                elif field == "scope":
                    scope = text.replace("Scope:", "").strip()
                elif field == "role":
                    role = text.replace("Role:", "").strip()
                elif field == "outcome":
                    outcomes.append(text)
                elif field == "responsibility":
                    responsibilities.append(text)
                elif field == "learning_outcome":
                    learning_outcomes.append(text)
                elif field == "tools":
                    tools.extend(t.strip() for t in text.replace("Tools:", "").split(",") if t.strip())
                elif field == "link" and r.get("url"):
                    if section == "certifications":
                        credentials.append(r["url"])
                    else:
                        links.append(r["url"])
                elif field == "course":
                    courses.append(text)
                elif field == "issuer":
                    issuer = text.replace("Issued by:", "").strip()

            if header:
                blocks.append(f"### {header}")
            if duration:
                blocks.append(f"- **{duration}**")
            if location:
                blocks.append(f"- **{location}**")
            if context:
                blocks.append(f"- **{context}**")

            if section == "education" and courses:
                blocks.append("- **Relevant coursework:**")
                for c in courses:
                    blocks.append(f"  - {c}")

            if section == "certifications":
                if issuer:
                    blocks.append(f"- **Issuer:** {issuer}")
                for url in credentials:
                    blocks.append(f"- **🔗 Credential:** [{url}]({url})")

            exp_type = next((r.get("experience_type") for r in items if r.get("experience_type")), None)

            if exp_type == "professional":
                if responsibilities:
                    blocks.append("- **Key responsibilities:**")
                    for r in responsibilities:
                        blocks.append(f"  - {r}")
            else:
                if learning_outcomes:
                    blocks.append("- **Key learning outcomes:**")
                    for l in learning_outcomes:
                        blocks.append(f"  - {l}")

            if description:
                blocks.append(f"- **Description:** {description}")
            if scope:
                blocks.append(f"- **Scope:** {scope}")
            if role:
                blocks.append(f"- **Role:** {role}")
            if outcomes:
                blocks.append("- **Key outcomes:**")
                for o in outcomes:
                    blocks.append(f"  - {o}")

            if tools:
                blocks.append(f"- **Technologies:** {', '.join(tools)}")

            for url in links:
                blocks.append(f"- **🔗GitHub:** [{url}]({url})")

            blocks.append("\n---\n")

        return "\n".join(blocks).strip()