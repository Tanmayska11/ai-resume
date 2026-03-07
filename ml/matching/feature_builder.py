#ml/matching/feature_builder.py

from typing import Dict, Any, List, Set
import re
import logging




logger = logging.getLogger(__name__)
# =====================================================
# Public API
# =====================================================

def build_features(
    resume: Dict[str, Any],
    job_description: str
) -> Dict[str, Any]:
    """
    Recruiter-safe, JD-centric feature builder.

    Core guarantees:
    - JD defines intent
    - Resume evidence can come from ANY section
    - Extra skills never inflate score blindly
    - Fully extensible with future DB updates
    """

    jd_text = _normalize_text(job_description)
        # 🔍 DEBUG — cleaned JD text
    print("\n========== DEBUG: CLEANED JD TEXT ==========")
    logger.debug("Cleaned JD text: %s", jd_text[:1000])
    print("===========================================\n")


    # ---------- JD understanding ----------
    jd_specialization = _jd_specialization_score(jd_text)
    jd_role_intent = _extract_jd_role_intent(jd_text)

    # ---------- Resume extraction ----------
    resume_skills = _extract_resume_skills(resume)
    resume_skill_levels = _extract_skill_levels(resume)

    experience_features = _experience_features(resume)
    education_features = _education_features(resume)
    project_features = _project_features(resume)

    resume_semantic_text = _build_resume_semantic_text(resume)
        # 🔍 DEBUG — resume semantic text
    print("\n========== DEBUG: RESUME SEMANTIC TEXT ==========")
    logger.debug("Resume semantic text: %s", resume_semantic_text[:1000])
    print("=================================================\n")

    resume_role_intent = _extract_resume_role_intent(resume)

    # ---------- JD-required skills ----------
    jd_required_skills = _extract_jd_skills(
        jd_text=jd_text,
        known_skill_vocab=resume_skills
    )

    # ---------- Skill matching ----------
    skill_match = _skill_match_features(
        resume_skills=resume_skills,
        resume_skill_levels=resume_skill_levels,
        jd_required_skills=jd_required_skills
    )

    # ---------- Semantic experience alignment ----------
    semantic_experience_score = _semantic_experience_score(
        resume_text=resume_semantic_text,
        jd_text=jd_text
    )

    # ---------- Role alignment ----------
    role_alignment_score = _role_alignment_score(
        jd_role=jd_role_intent,
        resume_role=resume_role_intent
    )

    return {
        # ================= Tier 1 (Primary drivers) =================
        "jd_skill_coverage": skill_match["coverage_ratio"],
        "avg_matched_skill_strength": skill_match["avg_strength"],
        "experience_years": experience_features["total_years"],
        "experience_constraint_met": experience_features["meets_jd_expectation"],
        "semantic_experience_score": semantic_experience_score,

        # ================= JD intent signals =================
        "jd_specialization_score": round(jd_specialization, 2),
        "role_alignment_score": round(role_alignment_score, 2),

        # ================= Tier 2 (Amplifiers) =================
        "project_relevance_score": project_features["relevance_score"],
        "tool_overlap_count": len(skill_match["matched_skills"]),

        # ================= Tier 3 (Trust & polish) =================
        "has_relevant_degree": education_features["has_relevant_degree"],
        "certification_count": education_features["certification_count"],

        # ================= Explainability =================
        "explain": {
            "matched_skills": skill_match["matched_skills"],
            "missing_required_skills": skill_match["missing_required_skills"],
            "additional_skills": skill_match["additional_skills"],

            "experience_summary": experience_features["summary"],
            "project_evidence": project_features["evidence"],
            "semantic_alignment": semantic_experience_score,
            "jd_role": jd_role_intent,
            "resume_role": resume_role_intent,
        }
    }


# =====================================================
# Resume Extractors
# =====================================================

def _extract_resume_skills(resume: Dict[str, Any]) -> Set[str]:
    return {
        s["name"].lower()
        for s in resume.get("skills", [])
        if s.get("name")
    }


def _extract_skill_levels(resume: Dict[str, Any]) -> Dict[str, float]:
    levels = {}
    for s in resume.get("skills", []):
        name = s.get("name")
        level = s.get("level", 0)
        if name:
            levels[name.lower()] = min(level / 100.0, 1.0)
    return levels


# =====================================================
# JD Skill Extraction (multi-source safe)
# =====================================================

def _extract_jd_skills(
    jd_text: str,
    known_skill_vocab: Set[str]
) -> Set[str]:

    matched = set()

    for skill in known_skill_vocab:
        skill_norm = skill.lower()

        if len(skill_norm) < 3:
            continue

        if skill_norm in jd_text:
            matched.add(skill)
            continue

        if _skill_alias_match(skill_norm, jd_text):
            matched.add(skill)

    return matched


def _skill_alias_match(skill: str, jd_text: str) -> bool:
    alias_map = {
        "apache airflow": ["airflow"],
        "aws (ec2, ecr)": ["aws", "amazon web services"],
        "etl / elt pipelines": ["etl", "elt", "data pipelines"],
        "git & github actions": ["git", "github", "ci cd", "cicd"],
        "fastapi / django rest": ["fastapi", "django", "rest api"],
        "pyspark": ["spark"],
        "machine learning (scikit-learn)": ["machine learning", "scikit learn"],
        "data modeling (relational)": ["data modeling", "relational modeling"],
        "data quality & validation": ["data quality", "data validation"],
    }

    for alias in alias_map.get(skill, []):
        if alias in jd_text:
            return True

    return False


# =====================================================
# Skill Matching
# =====================================================

def _skill_match_features(
    resume_skills: Set[str],
    resume_skill_levels: Dict[str, float],
    jd_required_skills: Set[str]
) -> Dict[str, Any]:

    matched = sorted(resume_skills & jd_required_skills)
    missing_required = sorted(jd_required_skills - resume_skills)
    additional = sorted(resume_skills - jd_required_skills)

    coverage_ratio = (
        len(matched) / len(jd_required_skills)
        if jd_required_skills else 0.0
    )

    avg_strength = (
        sum(resume_skill_levels.get(s, 0.6) for s in matched) / len(matched)
        if matched else 0.0
    )

    return {
        "coverage_ratio": round(coverage_ratio, 2),
        "avg_strength": round(avg_strength, 2),
        "matched_skills": matched,
        "missing_required_skills": missing_required[:3],
        "additional_skills": additional,
    }


# =====================================================
# Experience Features
# =====================================================

def _experience_features(resume: Dict[str, Any]) -> Dict[str, Any]:
    exp = resume.get("experience", {})
    total_years = exp.get("total_years", 0.0)

    summary = []
    if total_years >= 3:
        summary.append("Meets senior-level industry experience expectation")
    elif total_years >= 1:
        summary.append("Solid hands-on industry experience")
    else:
        summary.append("Early-stage professional experience")

    return {
        "total_years": total_years,
        "meets_jd_expectation": total_years >= 3.0,
        "summary": summary,
    }


# =====================================================
# Project Evidence
# =====================================================

def _project_features(resume: Dict[str, Any]) -> Dict[str, Any]:
    projects = resume.get("projects", {})
    count = projects.get("count", 0)

    relevance = min(count / 3.0, 1.0)

    evidence = []
    if count >= 2:
        evidence.append("Multiple end-to-end projects validating applied skills")

    return {
        "relevance_score": round(relevance, 2),
        "evidence": evidence,
    }


# =====================================================
# Education
# =====================================================

def _education_features(resume: Dict[str, Any]) -> Dict[str, Any]:
    degrees = [
        d.lower()
        for d in resume.get("education", {}).get("degrees", [])
        if d
    ]

    keywords = {"data", "engineering", "computer", "analytics", "science"}

    has_relevant_degree = any(
        any(k in degree for k in keywords)
        for degree in degrees
    )

    return {
        "has_relevant_degree": has_relevant_degree,
        "certification_count": len(resume.get("certifications", [])),
    }


# =====================================================
# Semantic Experience
# =====================================================

def _build_resume_semantic_text(resume: Dict[str, Any]) -> str:
    parts: List[str] = []

    def add(v):
        if v and isinstance(v, str):
            parts.append(v.lower())

    def add_many(values):
        for v in values:
            add(v)

    profile = resume.get("profile", {})
    add(profile.get("summary"))
    add_many(profile.get("target_roles", []))

    exp = resume.get("experience", {})
    add_many(exp.get("roles", []))
    add_many(exp.get("domains", []))
    add_many(exp.get("tools", []))

    projects = resume.get("projects", {})
    add_many(projects.get("types", []))
    add_many(projects.get("technologies", []))
    add_many(projects.get("outcomes", []))

    edu = resume.get("education", {})
    add_many(edu.get("degrees", []))

    return " ".join(parts)


def _semantic_experience_score(resume_text: str, jd_text: str) -> float:
    jd_tokens = set(jd_text.split())
    resume_tokens = set(resume_text.split())

    if not jd_tokens:
        return 0.0

    overlap = jd_tokens & resume_tokens
    return round(min(len(overlap) / len(jd_tokens), 1.0), 3)


# =====================================================
# Role Intent (CRITICAL FIX)
# =====================================================

def _extract_jd_role_intent(jd_text: str) -> str:
    if "data analyst" in jd_text:
        return "data_analyst"
    if "data scientist" in jd_text:
        return "data_scientist"
    if "machine learning" in jd_text or "ml engineer" in jd_text:
        return "ml_engineer"
    return "data_engineer"


def _extract_resume_role_intent(resume: Dict[str, Any]) -> str:
    roles = " ".join(resume.get("experience", {}).get("roles", [])).lower()
    summary = resume.get("profile", {}).get("summary", "").lower()

    text = roles + " " + summary

    if "data analyst" in text:
        return "data_analyst"
    if "data scientist" in text:
        return "data_scientist"
    if "machine learning" in text or "ml engineer" in text:
        return "ml_engineer"
    return "data_engineer"


def _role_alignment_score(jd_role: str, resume_role: str) -> float:
    if jd_role == resume_role:
        return 1.0
    if {jd_role, resume_role} <= {"data_engineer", "ml_engineer", "data_scientist","software_developer"}:
        return 0.8
    if jd_role == "data_analyst":
        return 0.5
    return 0.6


# =====================================================
# JD Specialization
# =====================================================

def _jd_specialization_score(jd_text: str) -> float:
    SPECIALIZED_KEYWORDS = {
        "mlops", "terraform", "rag", "feature store",
        "streaming", "kafka", "snowflake ml", "sagemaker"
    }

    hits = sum(1 for kw in SPECIALIZED_KEYWORDS if kw in jd_text)
    return min(hits / 5.0, 1.0)


# =====================================================
# Utilities
# =====================================================

def _normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()
