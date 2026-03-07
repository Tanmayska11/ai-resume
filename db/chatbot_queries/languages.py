# db/chatbot_queries/languages.py

from db.db import get_db_conn


def fetch_languages_context(user_id: str) -> list[dict]:
    """
    Fetch spoken languages and proficiency levels
    for chatbot grounding.
    """

    sql = """
        SELECT
            language,
            proficiency
        FROM languages
        WHERE user_id = %s
        ORDER BY language
    """

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()

    languages = []

    for language, proficiency in rows:
        languages.append({
            "language": language,
            "proficiency_level": proficiency,
        })

    return languages
