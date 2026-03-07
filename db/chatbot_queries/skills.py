# db/chatbot_queries/skills.py

from db.db import get_db_conn


def fetch_skills_context(user_id: str) -> list[dict]:
    """
    Fetch user skills with proficiency and category
    for chatbot grounding and ML feature usage.
    """

    sql = """
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

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()

    skills = []

    for skill_name, category, proficiency_level in rows:
        skills.append({
            "skill_name": skill_name,
            "category": category,
            "proficiency_level": proficiency_level,
        })

    return skills
