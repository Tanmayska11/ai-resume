import json
import psycopg2
from pathlib import Path
import re
import os

from dotenv import load_dotenv

load_dotenv()

# -----------------------------
# CONFIG
# -----------------------------
DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}



BASE_DIR = Path(__file__).resolve().parents[2]   # project root

RESUME_JSON_PATH = BASE_DIR / "resume" / "resume.json"

if not RESUME_JSON_PATH.exists():
    raise FileNotFoundError(f"resume.json not found at {RESUME_JSON_PATH}")


def parse_education_duration(duration: str):
    """
    Parses strings like:
    '2018 – 2021'
    'October 2024 – Present'
    """
    if not duration:
        return None, None

    years = re.findall(r"\d{4}", duration)

    if len(years) == 1:
        return int(years[0]), "present"

    if len(years) >= 2:
        return int(years[0]), years[1]

    return None, None


def normalize_date(value):
    """
    Converts YYYY-MM or YYYY-MM-DD to YYYY-MM-DD.
    Returns None for 'present' or null-like values.
    """
    if value is None:
        return None

    value = value.lower()

    if value in ("present", "current"):
        return None

    # YYYY-MM -> YYYY-MM-01
    if len(value) == 7:
        return f"{value}-01"

    # Already YYYY-MM-DD
    return value



# -----------------------------
# DB CONNECTION
# -----------------------------
def get_conn():
    return psycopg2.connect(
            **DB_CONFIG,
            options="-c client_encoding=UTF8"
        )


# -----------------------------
# MAIN SEED FUNCTION
# -----------------------------
def seed_resume():
    with open(RESUME_JSON_PATH, "r", encoding="utf-8") as f:
        resume = json.load(f)

    conn = get_conn()
    cur = conn.cursor()

    try:
        # =====================================================
        # 1. USER
        # =====================================================
        profile = resume["profile"]
        contact = profile["contact"]

        cur.execute("""
            INSERT INTO users (
                full_name, title, location, email, phone,
                linkedin_url, portfolio_url, summary
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING user_id
        """, (
            profile["name"],
            profile["title"],
            profile["location"],
            contact["email"],
            contact["phone"],
            contact["linkedin"],
            contact["portfolio"],
            profile["summary"]
        ))

        user_id = cur.fetchone()[0]

        # =====================================================
        # 2. SKILLS + USER_SKILLS
        # =====================================================
        for skill in resume["skills"]:
            cur.execute("""
                INSERT INTO skills (skill_name, category)
                VALUES (%s, %s)
                ON CONFLICT (skill_name) DO NOTHING
            """, (skill["name"], skill["category"]))

            cur.execute("""
                SELECT skill_id FROM skills WHERE skill_name = %s
            """, (skill["name"],))
            skill_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO user_skills (user_id, skill_id, proficiency_level)
                VALUES (%s, %s, %s)
                ON CONFLICT DO NOTHING
            """, (user_id, skill_id, skill["level"]))

        # =====================================================
        # 3. EXPERIENCE (PROFESSIONAL)
        # =====================================================
        for exp in resume["experience"]["professional_experience"]:
            cur.execute("""
                INSERT INTO experience (
                    user_id, experience_type, role, company,
                    location, context
                )
                VALUES (%s,'professional',%s,%s,%s,%s)
                RETURNING experience_id
            """, (
                user_id,
                exp["role"],
                exp["company"],
                exp["location"],
                exp["context"]
            ))

            exp_id = cur.fetchone()[0]

            for r in exp["responsibilities"]:
                cur.execute("""
                    INSERT INTO experience_responsibilities
                    (experience_id, responsibility)
                    VALUES (%s, %s)
                """, (exp_id, r))

            for t in exp["tools_used"]:
                cur.execute("""
                    INSERT INTO experience_tools
                    (experience_id, tool)
                    VALUES (%s, %s)
                """, (exp_id, t))

        # =====================================================
        # 4. EXPERIENCE (EXPERIMENTAL)
        # =====================================================
        for exp in resume["experience"]["experimental_experience"]:
            cur.execute("""
                INSERT INTO experience (
                    user_id, experience_type, role, context, notes
                )
                VALUES (%s,'experimental',%s,%s,%s)
                RETURNING experience_id
            """, (
                user_id,
                exp["area"],
                exp["context"],
                exp.get("note")
            ))

            exp_id = cur.fetchone()[0]

            for d in exp["details"]:
                cur.execute("""
                    INSERT INTO experience_responsibilities
                    (experience_id, responsibility)
                    VALUES (%s, %s)
                """, (exp_id, d))

            for t in exp["tools_used"]:
                cur.execute("""
                    INSERT INTO experience_tools
                    (experience_id, tool)
                    VALUES (%s, %s)
                """, (exp_id, t))

        # =====================================================
        # 5. PROJECTS
        # =====================================================
        for p in resume["projects"]:
            cur.execute("""
                INSERT INTO projects (
                    user_id, title, project_type,
                    description, scope, github_url, primary_role
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s)
                RETURNING project_id
            """, (
                user_id,
                p["title"],
                p["type"],
                p["description"],
                p["scope"],
                p["links"]["github"],
                p["role_alignment"]["primary"]
            ))

            project_id = cur.fetchone()[0]

            for o in p["outcomes"]:
                cur.execute("""
                    INSERT INTO project_outcomes
                    (project_id, outcome)
                    VALUES (%s, %s)
                """, (project_id, o))

            for tech in p["tech_stack"]:
                cur.execute("""
                    INSERT INTO project_tech_stack
                    (project_id, technology)
                    VALUES (%s, %s)
                """, (project_id, tech))

        # =====================================================
        # 6. EDUCATION
        # =====================================================
        for edu in resume["education"]:
            start_year, end_year = parse_education_duration(edu.get("duration"))

            cur.execute("""
                INSERT INTO education (
                    user_id,
                    degree,
                    institution,
                    location,
                    start_year,
                    end_year
                )
                VALUES (%s,%s,%s,%s,%s,%s)
                RETURNING education_id
            """, (
                user_id,
                edu["degree"],
                edu["institution"],
                edu["location"],
                start_year,
                end_year
            ))


            edu_id = cur.fetchone()[0]

            for c in edu.get("courses", []):
                cur.execute("""
                    INSERT INTO education_courses
                    (education_id, course_title, grade)
                    VALUES (%s, %s, %s)
                """, (edu_id, c["title"], c["grade"]))

        # =====================================================
        # 7. CERTIFICATIONS
        # =====================================================
        for cert in resume["certifications"]:
            cur.execute("""
                INSERT INTO certifications
                (user_id, name, issuer, credential_url)
                VALUES (%s,%s,%s,%s)
            """, (
                user_id,
                cert["name"],
                cert["issuer"],
                cert["credential_url"]
            ))

        # =====================================================
        # 8. LANGUAGES
        # =====================================================
        for lang in resume["languages"]:
            cur.execute("""
                INSERT INTO languages
                (user_id, language, proficiency)
                VALUES (%s,%s,%s)
            """, (
                user_id,
                lang["language"],
                lang["proficiency"]
            ))

        # =====================================================
        # 9. CAREER PREFERENCES
        # =====================================================
        prefs = resume["career_preferences"]
        cur.execute("""
            INSERT INTO career_preferences
            (user_id, target_roles, preferred_locations, work_type)
            VALUES (%s,%s,%s,%s)
        """, (
            user_id,
            prefs["target_roles"],
            prefs["preferred_locations"],
            prefs["work_type"]
        ))

        # =====================================================
        # 10. CAREER TIMELINE
        # =====================================================
        for t in resume["career_timeline"]:
            cur.execute("""
                INSERT INTO career_timeline
                (user_id, label, start_period, end_period, timeline_type)
                VALUES (%s,%s,%s,%s,%s)
            """, (
                user_id,
                t["label"],
                normalize_date(t["start"]),
                normalize_date(t["end"]),
                t["type"]
            ))


        conn.commit()
        print("✅ Resume data seeded successfully")

    except Exception as e:
        conn.rollback()
        print("❌ Error during seeding:", e)
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    seed_resume()
