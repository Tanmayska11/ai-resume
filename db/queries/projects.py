from db.db import get_db_conn


def fetch_projects(limit: int = 4):
    query = """
        SELECT
            title,
            github_url
        FROM projects
        ORDER BY title
        LIMIT %s;
    """

    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute(query, (limit,))
        rows = cur.fetchall()

    return [
        {
            "title": title,
            "github": github_url
        }
        for title, github_url in rows
    ]
