# db/chatbot_queries/extracurricular_activities.py

from db.db import get_db_conn


def fetch_extracurricular_activities_context(user_id: str) -> list[dict]:
    """
    Fetch spoken languages and proficiency levels
    for chatbot grounding.
    """

    sql = """
        SELECT
            activity           
        FROM extracurricular_activities
        WHERE user_id = %s
        ORDER BY activity
        
    """

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()

    activities = []

    for (activity,) in rows:
        activities.append({
            "activity": activity,
            
        })

    return activities
