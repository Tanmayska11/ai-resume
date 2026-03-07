# db/chatbot_queries/certifications.py

from db.db import get_db_conn


def fetch_certifications_context(user_id: str) -> list[dict]:
    """
    Fetch certifications for chatbot grounding.
    """

    sql = """
        SELECT
            certification_id,
            certificate_name,
            issuer,
            credential_url
        FROM certifications
        WHERE user_id = %s
        ORDER BY issuer, certificate_name
    """

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()

    certifications = []

    for certification_id, certificate_name, issuer, credential_url in rows:
        certifications.append({
            "certification_id": certification_id,
            "certificate_name": certificate_name,
            "issuer": issuer,
            "credential_url": credential_url,
        })


    return certifications
