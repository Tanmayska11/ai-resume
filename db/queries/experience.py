#queries/experience.py

from db.db import get_db_conn
from datetime import datetime





def fetch_professional_experience():
    query = """
        SELECT
            role,
            company,
            location,
            start_date,
            end_date,
            context
        FROM experience
        WHERE experience_type = 'professional'
        ORDER BY company DESC;
    """

    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()

    experiences = []

    for row in rows:
        startraw, endraw = row[3], row[4]

        start = datetime.strptime(startraw, "%B - %Y")
        end = datetime.strptime(endraw, "%B - %Y")

       
             

        # Compute duration string (UI concern, not DB)
        if start and end:
            duration = f"{start.strftime('%b %Y')} - {end.strftime('%b %Y')}"
        elif start:
            duration = f"{start.strftime('%b %Y')} - Present"
        else:
            duration = ""

        experiences.append({
            "role": row[0],
            "company": row[1],
            "location": row[2],
            "duration": duration,
            "context": row[5],
        })

    return experiences



