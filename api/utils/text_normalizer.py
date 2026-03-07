import re


def normalize_job_description(text: str) -> str:
    """
    Cleans pasted JDs, PDFs, DOCs, LinkedIn posts.
    Output: clean lowercase text
    """
    if not text:
        return ""

    # Normalize newlines
    text = text.replace("\r", "\n")

    # Remove bullets & symbols
    text = re.sub(r"[•▪●◆▶➤✔️]", " ", text)

    # Remove weird unicode but keep meaning
    text = re.sub(r"[^\w\s.,:+\-()]", " ", text)

    # Normalize spacing
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()
