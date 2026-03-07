# ml/matching/scorer.py

from typing import Dict, Any


# =====================================================
# Scoring Configuration
# =====================================================

WEIGHTS = {
    # ---------- Tier 1: Core decision drivers ----------
    "skill_coverage": 0.28,
    "skill_strength": 0.10,
    "experience": 0.18,
    "semantic_experience": 0.20,
    "role_alignment": 0.09,

    # ---------- Tier 2: Amplifiers ----------
    "tools_projects": 0.10,

    # ---------- Tier 3: Trust ----------
    "education_cert": 0.05,
}

# Floors (protect strong profiles)
MIN_SCORE_IF_CORE_MATCH = 65
MIN_SCORE_IF_STRONG_PROFILE = 80

# Caps (prevent inflation)
MAX_SCORE_FOR_ROLE_MISMATCH = 75
MAX_SCORE_FOR_EXTRA_SKILL_DOMINANCE = 85


# =====================================================
# Public API
# =====================================================

def score_match(features: Dict[str, Any]) -> Dict[str, Any]:

    # ================= Tier 1 =================
    skill_coverage_score = features["jd_skill_coverage"] * 100
    skill_strength_score = features["avg_matched_skill_strength"] * 100

    experience_years = features["experience_years"]
    experience_score = min(experience_years / 3.0, 1.0) * 100

    semantic_experience_score = features.get(
        "semantic_experience_score", 0.0
    ) * 100

    role_alignment_score = features.get(
        "role_alignment_score", 0.6
    ) * 100

    # ================= Tier 2 =================
    tools_projects_score = features["project_relevance_score"] * 100

    # ================= Tier 3 =================
    education_cert_score = (
        (1 if features["has_relevant_degree"] else 0) * 60
        + min(features["certification_count"], 3) * 10
    )
    education_cert_score = min(education_cert_score, 100)

    # ================= Weighted aggregation =================
    raw_score = (
        WEIGHTS["skill_coverage"] * skill_coverage_score
        + WEIGHTS["skill_strength"] * skill_strength_score
        + WEIGHTS["experience"] * experience_score
        + WEIGHTS["semantic_experience"] * semantic_experience_score
        + WEIGHTS["role_alignment"] * role_alignment_score
        + WEIGHTS["tools_projects"] * tools_projects_score
        + WEIGHTS["education_cert"] * education_cert_score
    )

    # ================= JD specialization guard =================
    jd_spec = features.get("jd_specialization_score", 0.0)
    semantic_exp = features.get("semantic_experience_score", 0.0)

    if jd_spec >= 0.6 and semantic_exp < 0.4:
        raw_score = min(raw_score, 80)

    # ================= Extra-skill dominance =================
    if skill_coverage_score >= 85 and semantic_experience_score < 45:
        raw_score = min(raw_score, MAX_SCORE_FOR_EXTRA_SKILL_DOMINANCE)

    # ================= Role mismatch cap =================
    if role_alignment_score < 60:
        raw_score = min(raw_score, MAX_SCORE_FOR_ROLE_MISMATCH)

    # ================= Safety floors =================
    if (
        skill_coverage_score >= 65
        and experience_score >= 60
        and raw_score < MIN_SCORE_IF_CORE_MATCH
    ):
        raw_score = MIN_SCORE_IF_CORE_MATCH

    if (
        semantic_experience_score >= 60
        and skill_coverage_score >= 60
        and raw_score < MIN_SCORE_IF_STRONG_PROFILE
    ):
        raw_score = MIN_SCORE_IF_STRONG_PROFILE

    final_score = round(raw_score, 1)

    explanation = _build_explanation(final_score, features)

    return {
        "score": final_score,
        "band": _score_band(final_score),
        "explanation": explanation,
    }


# =====================================================
# Score Band Mapping (YOUR SCALE)
# =====================================================

def _score_band(score: float) -> str:
    if score >= 90:
        return "Exceptional / Near-ideal match"
    if score >= 80:
        return "Very strong match"
    if score >= 70:
        return "Strong match"
    if score >= 60:
        return "Aligned"
    if score >= 55:
        return "Not aligned"
    return "Not a match"


# =====================================================
# Explanation Builder
# =====================================================

def _build_explanation(score: float, features: Dict[str, Any]) -> Dict[str, Any]:

    strengths = []
    gaps = []
    recommendations = []

    matched_skills = features["explain"]["matched_skills"]
    additional_skills = features["explain"]["additional_skills"]
    missing_required = features["explain"]["missing_required_skills"]

    jd_role = features["explain"].get("jd_role")
    resume_role = features["explain"].get("resume_role")

    # ---------- Strengths ----------
    if features["jd_skill_coverage"] >= 0.6 and matched_skills:
        strengths.append(
            f"Strong alignment with core required skills: {', '.join(matched_skills)}"
        )

    if features["experience_years"] >= 3:
        strengths.append(
            "Profile Meets senior-level experience expectations with strong hands-on industry background"
        )
    elif features["experience_years"] >= 1.5:
        strengths.append(
            "Tanmay has Solid hands-on industry experience relevant to the role"
        )

    if features.get("semantic_experience_score", 0) >= 0.45:
        strengths.append(
            "Demonstrates relevant experience aligned with role responsibilities"
        )

    if additional_skills:
        strengths.append(
            "Brings additional technical capabilities beyond core requirements"
        )

    # ---------- Gaps ----------
    if missing_required:
        gaps.append(
            f"Some required skills are not yet demonstrated: "
            f"{', '.join(missing_required[:3])}"
        )

    if jd_role and resume_role and jd_role != resume_role:
        gaps.append(
            f"Primary experience aligns more closely with {resume_role.replace('_', ' ')} roles"
        )

    # ---------- Recommendations ----------
    if missing_required:
        recommendations.append(
            "Add or highlight hands-on examples demonstrating the missing required skills"
        )

    if features["project_relevance_score"] < 0.6:
        recommendations.append(
            "Highlight or add one backend-heavy end-to-end project"
        )

    return {
        "strengths": strengths,
        "gaps": gaps,
        "recommendations": recommendations,
        "summary": _score_band(score),
    }
