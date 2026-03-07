from langdetect import detect, LangDetectException


def detect_language(text: str) -> str:
    """
    Returns 'en', 'de', or 'unknown'
    """
    try:
        lang = detect(text)
        if lang in {"en", "de"}:
            return lang
        return "unknown"
    except LangDetectException:
        return "unknown"
