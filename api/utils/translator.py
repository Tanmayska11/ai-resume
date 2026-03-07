from deep_translator import GoogleTranslator


def translate_to_english(text: str, source_lang: str) -> str:
    """
    Translates DE → EN
    English stays unchanged
    """
    if not text:
        return ""

    if source_lang == "en":
        return text

    try:
        return GoogleTranslator(source=source_lang, target="en").translate(text)
    except Exception:
        # Fail-safe: return original
        return text
