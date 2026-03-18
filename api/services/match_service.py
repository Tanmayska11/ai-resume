from typing import Dict, Any
from uuid import UUID

from db.db import get_db_conn
from db.queries.job_match import fetch_resume_for_matching

from api.utils.text_normalizer import normalize_job_description
from api.utils.language import detect_language
from api.utils.translator import translate_to_english

import logging
from fastapi import UploadFile
import pdfplumber
import docx

logger = logging.getLogger(__name__)

# Single-user portfolio system (intentional)
PORTFOLIO_USER_ID = UUID("6593eba4-0118-4e49-ba9c-c2b6a9e879cf")

# 🔥 GLOBAL CACHE (IMPORTANT)
_build_features = None
_score_match = None


def extract_text_from_file(file: UploadFile) -> str:
    filename = file.filename.lower()

    if filename.endswith(".pdf"):
        with pdfplumber.open(file.file) as pdf:
            return "\n".join(
                page.extract_text() or "" for page in pdf.pages
            )

    if filename.endswith(".docx") or filename.endswith(".doc"):
        document = docx.Document(file.file)
        return "\n".join(p.text for p in document.paragraphs)

    return ""


def get_ml_modules():
    """
    Lazy load ML modules ONLY when needed.
    Prevents slow startup and Render timeouts.
    """
    global _build_features, _score_match

    if _build_features is None or _score_match is None:
        print("🔥 Loading ML modules (first time only)...")

        from ml.matching.feature_builder import build_features
        from ml.matching.scorer import score_match

        _build_features = build_features
        _score_match = score_match

    return _build_features, _score_match


async def evaluate_resume_job_match(
    job_description: str,
    file: UploadFile | None = None,
) -> Dict[str, Any]:

    print("\n========== DEBUG: RAW USER INPUT ==========")
    logger.info("Received job description input")
    logger.debug("RAW USER INPUT (first 1000 chars): %s", job_description[:1000])
    print("===========================================\n")

    extracted_text = ""

    if file:
        extracted_text = extract_text_from_file(file)

    final_jd = "\n\n".join(
        part for part in [job_description.strip(), extracted_text.strip()] if part
    )

    if not final_jd:
        raise ValueError("Job description is empty")

    # =====================================================
    # 1️⃣ Normalize input
    # =====================================================
    normalized_jd = normalize_job_description(final_jd)

    # =====================================================
    # 2️⃣ Detect language
    # =====================================================
    detected_lang = detect_language(normalized_jd)

    # =====================================================
    # 3️⃣ Translate if needed
    # =====================================================
    jd_in_english = translate_to_english(
        text=normalized_jd,
        source_lang=detected_lang
    )

    # =====================================================
    # 4️⃣ Fetch resume
    # =====================================================
    with get_db_conn() as conn:
        resume = fetch_resume_for_matching(conn, PORTFOLIO_USER_ID)

        if not resume:
            raise ValueError("Resume not found")

    # =====================================================
    # 5️⃣ Lazy load ML (CRITICAL FIX)
    # =====================================================
    build_features, score_match = get_ml_modules()

    # =====================================================
    # 6️⃣ Feature extraction
    # =====================================================
    features = build_features(
        resume=resume,
        job_description=jd_in_english,
    )

    # =====================================================
    # 7️⃣ Scoring
    # =====================================================
    result = score_match(features)
    explanation = result["explanation"]

    # =====================================================
    # 8️⃣ Response
    # =====================================================
    return {
        "match_score": result["score"],
        "strengths": explanation["strengths"],
        "gaps": explanation["gaps"],
        "recommendations": explanation["recommendations"],
        "summary": explanation["summary"],
    }