from db.db import get_db_conn


def fetch_skills(limit: int = 8):
    query = """
        SELECT
            s.skill_name,
            us.proficiency_level
        FROM user_skills us
        JOIN skills s ON us.skill_id = s.skill_id
        ORDER BY us.proficiency_level DESC
        LIMIT %s;
    """

    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, (limit,))
        rows = cur.fetchall()

    return [
        {
            "name": name,
            "level": level
        }
        for name, level in rows
    ]
