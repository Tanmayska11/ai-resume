from db.db import get_db_conn


def fetch_profile():
    query = """
        SELECT
            full_name,
            title,
            location,
            summary,
            email,
            phone,
            linkedin_url,
            portfolio_url
        FROM users
        LIMIT 1;
    """

    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute(query)
        row = cur.fetchone()

    if not row:
        raise RuntimeError("No profile data found in database")

    return {
        "name": row[0],
        "title": row[1],
        "location": row[2],
        "summary": row[3],
        "contact": {
            "email": row[4],
            "phone": row[5],
            "linkedin": row[6],
            "portfolio": row[7],
        },
    }
