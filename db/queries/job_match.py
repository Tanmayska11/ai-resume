# db/queries/job_match.py

from datetime import date, datetime
from typing import Dict, List, Any
from typing import Optional


MONTH_YEAR_FORMATS = [
    "%B - %Y",   # May - 2021
    "%b - %Y",   # May - 2021 (short month, just in case)
]


def parse_month_year_safe(value: Optional[str]) -> Optional[date]:
    """
    Parse TEXT date values like:
    - 'May - 2021'
    - 'December - 2023'
    - 'Present'
    Returns a date object (1st day of month) or None.
    """

    if not value:
        return None

    value = value.strip().lower()

    if value in {"present", "current", "now"}:
        return date.today()

    for fmt in MONTH_YEAR_FORMATS:
        try:
            return datetime.strptime(value.title(), fmt).date()
        except ValueError:
            continue

    return None


# ===============================
# Public API
# ===============================

def fetch_resume_for_matching(conn, user_id: int) -> Dict[str, Any]:
    """
    Fetch a normalized, feature-ready snapshot of a user's resume
    for Resume–Job matching.

    This function is intentionally deterministic and ML-friendly.
    """
    resume = {
        "profile": _fetch_profile(conn, user_id),
        "skills": _fetch_skills(conn, user_id),
        "experience": _fetch_experience(conn, user_id),
        "projects": _fetch_projects(conn, user_id),
        "education": _fetch_education(conn, user_id),
        "certifications": _fetch_certifications(conn, user_id),
        "languages": _fetch_languages(conn, user_id),
    }


    # print("\n========== DEBUG: RESUME SNAPSHOT ==========")

    # # -------------------------------
    # # Profile
    # # -------------------------------
    # print("\n[PROFILE]")
    # for k, v in resume.get("profile", {}).items():
    #     print(f"{k}: {v}")

    # # -------------------------------
    # # Skills
    # # -------------------------------
    # print("\n[SKILLS]")
    # print("Count:", len(resume["skills"]))
    # print("Names:", [s["name"] for s in resume["skills"]])
    # print("With levels:", [(s["name"], s["level"]) for s in resume["skills"]])

    # # -------------------------------
    # # Experience
    # # -------------------------------
    # print("\n[EXPERIENCE]")
    # exp = resume["experience"]
    # print("Total years:", exp.get("total_years"))
    # print("Roles:", exp.get("roles"))
    # print("Tools:", exp.get("tools"))
    # print("Domains:", exp.get("domains"))

    # # -------------------------------
    # # Projects
    # # -------------------------------
    # print("\n[PROJECTS]")
    # proj = resume["projects"]
    # print("Project count:", proj.get("count"))
    # print("Types:", proj.get("types"))
    # print("Technologies:", proj.get("technologies"))
    # print("Outcomes:", proj.get("outcomes"))

    # # -------------------------------
    # # Education
    # # -------------------------------
    # print("\n[EDUCATION]")
    # edu = resume["education"]
    # print("Degrees:", edu.get("degrees"))
    # print("Institutions:", edu.get("institutions"))
    # print("Fields / Courses:", edu.get("fields"))

    # # -------------------------------
    # # Certifications
    # # -------------------------------
    # print("\n[CERTIFICATIONS]")
    # print("Count:", len(resume["certifications"]))
    # print("Certificates:", resume["certifications"])

    # # -------------------------------
    # # Languages
    # # -------------------------------
    # print("\n[LANGUAGES]")
    # for lang in resume["languages"]:
    #     print(f"{lang['language']} - {lang['proficiency']}")

    # print("\n===========================================\n")


    return resume




# ===============================
# Profile & Career Intent
# ===============================

def _fetch_profile(conn, user_id: int) -> Dict[str, Any]:
    query = """
        SELECT
            u.title,
            u.location,
            u.summary,
            cp.target_roles,
            cp.preferred_locations,
            cp.work_type
        FROM users u
        LEFT JOIN career_preferences cp
            ON u.user_id = cp.user_id
        WHERE u.user_id = %s
    """

    with conn.cursor() as cur:
        cur.execute(query, (user_id,))
        row = cur.fetchone()

    if not row:
        return {}

    return {
        "title": row[0],
        "location": row[1],
        "summary": row[2],
        "target_roles": row[3] or [],
        "preferred_locations": row[4] or [],
        "work_type": row[5],
    }


# ===============================
# Skills
# ===============================

def _fetch_skills(conn, user_id: int) -> List[Dict[str, Any]]:
    query = """
        SELECT
            s.skill_name,
            s.category,
            us.proficiency_level
        FROM user_skills us
        JOIN skills s
            ON us.skill_id = s.skill_id
        WHERE us.user_id = %s
        ORDER BY us.proficiency_level DESC, s.skill_name
    """

    with conn.cursor() as cur:
        cur.execute(query, (user_id,))
        rows = cur.fetchall()

    return [
        {
            "name": r[0],
            "category": r[1],
            "level": r[2],
        }
        for r in rows
    ]


# ===============================
# Experience (Aggregated)
# ===============================

def _fetch_experience(conn, user_id: str) -> Dict[str, Any]:
    query = """
        SELECT
            e.experience_id,
            e.start_date,
            e.end_date,
            e.role,
            er.learning_outcomes,
            et.tool
        FROM experience e
        LEFT JOIN experience_responsibilities er
            ON e.experience_id = er.experience_id
        LEFT JOIN experience_tools et
            ON e.experience_id = et.experience_id
        WHERE e.user_id = %s
    """

    with conn.cursor() as cur:
        cur.execute(query, (user_id,))
        rows = cur.fetchall()

    roles = set()
    tools = set()
    domains = set()

    # 🔑 duration must be counted ONCE per experience_id
    experience_ranges = {}

    for exp_id, start_date, end_date, role, learning, tool in rows:
        if role:
            roles.add(role)

        if tool:
            tools.add(tool)

        if learning:
            domains.add(learning)

        if exp_id not in experience_ranges:
            start = parse_month_year_safe(start_date)
            end = parse_month_year_safe(end_date) or date.today()

            if start:
                experience_ranges[exp_id] = (start, end)

    total_days = sum(
        max((end - start).days, 0)
        for start, end in experience_ranges.values()
    )

    total_years = round(total_days / 365.25, 1)

    return {
        "total_years": total_years,
        "roles": sorted(roles),
        "tools": sorted(tools),
        "domains": sorted(domains),
    }



# ===============================
# Projects
# ===============================

def _fetch_projects(conn, user_id: int) -> Dict[str, Any]:
    query = """
        SELECT
            p.project_type,
            po.outcome,
            pts.technology
        FROM projects p
        LEFT JOIN project_outcomes po
            ON p.project_id = po.project_id
        LEFT JOIN project_tech_stack pts
            ON p.project_id = pts.project_id
        WHERE p.user_id = %s
    """

    with conn.cursor() as cur:
        cur.execute(query, (user_id,))
        rows = cur.fetchall()

    project_types = set()
    technologies = set()
    outcomes = set()

    for project_type, outcome, technology in rows:
        if project_type:
            project_types.add(project_type)
        if technology:
            technologies.add(technology)
        if outcome:
            outcomes.add(outcome)

    return {
        "count": len(project_types),
        "types": sorted(project_types),
        "technologies": sorted(technologies),
        "outcomes": sorted(outcomes),
    }


# ===============================
# Education
# ===============================

def _fetch_education(conn, user_id: int) -> Dict[str, Any]:
    query = """
        SELECT
            e.degree,
            e.institution,
            ec.course_title
        FROM education e
        LEFT JOIN education_courses ec
            ON e.education_id = ec.education_id
        WHERE e.user_id = %s
    """

    with conn.cursor() as cur:
        cur.execute(query, (user_id,))
        rows = cur.fetchall()

    degrees = set()
    institutions = set()
    fields = set()

    for degree, institution, course in rows:
        if degree:
            degrees.add(degree)
        if institution:
            institutions.add(institution)
        if course:
            fields.add(course)

    return {
        "degrees": sorted(degrees),
        "institutions": sorted(institutions),
        "fields": sorted(fields),
    }


# ===============================
# Certifications
# ===============================

def _fetch_certifications(conn, user_id: int) -> List[str]:
    query = """
        SELECT certificate_name
        FROM certifications
        WHERE user_id = %s
        ORDER BY certificate_name
    """

    with conn.cursor() as cur:
        cur.execute(query, (user_id,))
        rows = cur.fetchall()

    return [r[0] for r in rows]


# ===============================
# Languages
# ===============================

def _fetch_languages(conn, user_id: int) -> List[Dict[str, str]]:
    query = """
        SELECT language, proficiency
        FROM languages
        WHERE user_id = %s
        ORDER BY language
    """

    with conn.cursor() as cur:
        cur.execute(query, (user_id,))
        rows = cur.fetchall()

    return [
        {"language": r[0], "proficiency": r[1]}
        for r in rows
    ]



