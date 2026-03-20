import threading

USER_ID = "6593eba4-0118-4e49-ba9c-c2b6a9e879cf"


class IndexManager:
    _lock = threading.Lock()
    _is_rebuilding = False

    @classmethod
    def rebuild(cls):
        if cls._is_rebuilding:
            return

        with cls._lock:
            cls._is_rebuilding = True
            try:
                # 🔥 lazy import
                from chatbot.embeddings.build_index import build_faiss_index

                build_faiss_index(USER_ID)
                cls._invalidate_retriever()
            finally:
                cls._is_rebuilding = False

    @staticmethod
    def _invalidate_retriever():
        # 🔥 lazy import (avoid circular + heavy load at startup)
        from chatbot.service import ResumeChatbotService
        ResumeChatbotService.invalidate()