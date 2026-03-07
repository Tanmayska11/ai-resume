# db/chatbot_queries/education.py

from db.db import get_db_conn


def fetch_education_context(user_id: str) -> list[dict]:
    """
    Fetch education history with optional coursework
    for chatbot grounding and narrative generation.
    """

    sql = """
        SELECT
            e.education_id,
            e.degree,
            e.institution,
            e.location,
            e.start_year,
            e.end_year,
            ec.course_title,
            ec.grade
        FROM education e
        LEFT JOIN education_courses ec
            ON e.education_id = ec.education_id
        WHERE e.user_id = %s
        ORDER BY e.start_year ASC
    """

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()

    edu_map = {}

    for row in rows:
        (
            education_id,
            degree,
            institution,
            location,
            start_year,
            end_year,
            course_title,
            grade,
        ) = row

        if education_id not in edu_map:
            edu_map[education_id] = {
                "degree": degree,
                "institution": institution,
                "location": location,
                "start_year": start_year,
                "end_year": end_year,
                "courses": [],
            }

        if course_title:
            edu_map[education_id]["courses"].append({
                "title": course_title,
                "grade": grade,
            })

    education = []

    for education_id, edu in edu_map.items():
        education.append({
            "education_id": education_id,  
            "degree": edu["degree"],
            "institution": edu["institution"],
            "location": edu["location"],
            "start_year": edu["start_year"],
            "end_year": edu["end_year"] or "Present",
            "relevant_coursework": edu["courses"],
        })


    return education
