from db.db import get_db_conn
from datetime import date, datetime


def _to_yyyy_mm(value):
    """
    Normalize DATE | datetime | str | None → 'YYYY-MM' or 'present'
    """
    if value is None:
        return "present"

    # psycopg2 may return DATE as date or str
    if isinstance(value, date):
        return value.strftime("%Y-%m")

    if isinstance(value, datetime):
        return value.strftime("%Y-%m")

    if isinstance(value, str):
        # Handles 'YYYY-MM-DD' or 'YYYY-MM'
        return value[:7]

    raise TypeError(f"Unsupported date type: {type(value)}")


def fetch_career_timeline():
    query = """
        SELECT
            label,
            start_period,
            end_period,
            timeline_type
        FROM career_timeline
        ORDER BY start_period;
    """

    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute(query)
        rows = cur.fetchall()

    events = []

    for label, start, end, ttype in rows:
        events.append({
            "label": label,
            "start": _to_yyyy_mm(start),
            "end": _to_yyyy_mm(end),
            "type": ttype,
        })

    return events
