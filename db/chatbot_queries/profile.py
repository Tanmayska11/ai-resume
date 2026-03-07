# db/chatbot_queries/profile.py

from db.db import get_db_conn


def fetch_profile_context(user_id: str) -> dict:
    """
    Fetch high-level profile and career intent.
    This is the root context for the chatbot.
    """

    sql = """
        SELECT
            u.full_name,
            u.title,
            u.location,
            u.email,
            u.linkedin_url,
            u.portfolio_url,
            u.summary,
            cp.target_roles,
            cp.preferred_locations,
            cp.work_type
        FROM users u
        LEFT JOIN career_preferences cp
            ON u.user_id = cp.user_id
        WHERE u.user_id = %s
    """

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            row = cur.fetchone()

    if not row:
        return {}

    (
        full_name,
        title,
        location,
        email,
        linkedin,
        portfolio,
        summary,
        target_roles,
        preferred_locations,
        work_type,
    ) = row

    return {
        
            "name": full_name,
            "title": title,
            "location": location,
            "summary": summary,
            "contact": {
                "email": email,
                "linkedin": linkedin,
                "portfolio": portfolio,
        },
        "career_preferences": {
            "target_roles": target_roles or [],
            "preferred_locations": preferred_locations or [],
            "work_type": work_type or [],
        },
    }
