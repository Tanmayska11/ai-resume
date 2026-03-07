# db/chatbot_queries/projects.py

from db.db import get_db_conn


def fetch_projects_context(user_id: str) -> list[dict]:
    """
    Fetch full project context for chatbot usage:
    - core project details
    - outcomes
    - tech stack
    Aggregated into clean narrative units.
    """

    sql = """
        SELECT
            p.project_id,
            p.title,
            p.project_type,
            p.description,
            p.scope,
            p.github_url,
            p.primary_role,
            po.outcome,
            pts.technology
        FROM projects p
        LEFT JOIN project_outcomes po
            ON p.project_id = po.project_id
        LEFT JOIN project_tech_stack pts
            ON p.project_id = pts.project_id
        WHERE p.user_id = %s
        ORDER BY
            p.project_type, 
            p.title
    """

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()

    project_map = {}

    for row in rows:
        (
            project_id,
            title,
            project_type,
            description,
            scope,
            github_url,
            primary_role,
            outcome,
            technology,
        ) = row

        if project_id not in project_map:
            project_map[project_id] = {
                "title": title,
                "project_type": project_type,
                "description": description,
                "scope": scope,
                "primary_role": primary_role,
                "github_url": github_url,
                "outcomes": set(),
                "tech_stack": set(),
            }

        if outcome:
            project_map[project_id]["outcomes"].add(outcome)

        if technology:
            project_map[project_id]["tech_stack"].add(technology)

    projects = []

    for project in project_map.values():
        projects.append({
            "title": project["title"],
            "project_type": project["project_type"],
            "description": project["description"],
            "scope": project["scope"],
            "primary_role": project["primary_role"],
            "github_url": project["github_url"],
            "key_outcomes": sorted(project["outcomes"]),
            "technologies_used": sorted(project["tech_stack"]),
        })

    return projects
