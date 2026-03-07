# db/chatbot_queries/experience.py

from collections import defaultdict
from db.db import get_db_conn


def fetch_experience_context(user_id: str) -> list[dict]:
    """
    Fetch full experience context for chatbot:
    - experience
    - responsibilities
    - tools
    Aggregated into narrative blocks.
    """

    sql = """
        SELECT
            e.experience_id,
            e.experience_type,
            e.role,
            e.company,
            e.location,
            e.start_date,
            e.end_date,
            e.context,
            er.responsibility,
            er.learning_outcomes,
            et.tool
        FROM experience e
        LEFT JOIN experience_responsibilities er
            ON e.experience_id = er.experience_id
        LEFT JOIN experience_tools et
            ON e.experience_id = et.experience_id
        WHERE e.user_id = %s
        ORDER BY
            e.experience_type DESC,
            e.start_date DESC

        """

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()

    experience_map = {}

    for row in rows:
        (
            exp_id,
            exp_type,
            role,
            company,
            location,
            start_date,
            end_date,
            context,            
            responsibility,
            learning_outcomes,
            tool,
        ) = row

        if exp_id not in experience_map:
            experience_map[exp_id] = {
                "experience_type": exp_type,
                "role": role,
                "company": company,
                "location": location,
                "start_date": start_date,
                "end_date": end_date,
                "context": context,                
                "responsibilities": set(),
                "learning_outcomes": set(),
                "tools": set(),
            }

        if responsibility:
            experience_map[exp_id]["responsibilities"].add(responsibility)
        
        if learning_outcomes:
            experience_map[exp_id]["learning_outcomes"].add(learning_outcomes)

        if tool:
            experience_map[exp_id]["tools"].add(tool)

    # Final clean structure
    experiences = []

    for exp in experience_map.values():
        experiences.append({
            "experience_type": exp["experience_type"],
            "role": exp["role"],
            "company": exp["company"],
            "location": exp["location"],
            "duration": {
                "start_date": exp["start_date"],
                "end_date": exp["end_date"] or "Present",
            },
            "summary": exp["context"],
            "key_responsibilities": sorted(exp["responsibilities"]),
            "learning_outcomes": sorted(exp["learning_outcomes"]),
            "tools_used": sorted(exp["tools"]),
        })

    return experiences
