from db.db import get_db_conn


def fetch_latest_education():
    """
    Fetch the most recent (highest start_year) education entry.
    """
    query = """
        SELECT
            degree,
            institution,
            location,
            start_year,
            end_year
        FROM education
        ORDER BY start_year DESC
        LIMIT 1;
    """

    with get_db_conn() as conn:
        cur = conn.cursor()
        cur.execute(query)
        row = cur.fetchone()

    if not row:
        raise RuntimeError("No education data found")

    degree, institution, location, start_year, end_year = row

    # ---- duration formatting (UI-friendly) ----
    if end_year is None or end_year.lower() == "present":
        duration = f"{start_year} – Present"
    else:
        duration = f"{start_year} – {end_year}"

    return {
        "degree": degree,
        "institution": institution,
        "location": location,
        "duration": duration,
    }
