"""
Fetch and normalize GitHub README files
for chatbot grounding.
"""

import requests
from typing import List, Dict
from urllib.parse import urlparse

GITHUB_RAW_BASE = "https://raw.githubusercontent.com"
REQUEST_TIMEOUT = 10


def _parse_repo_owner_and_name(repo_url: str) -> tuple[str, str] | None:
    try:
        parsed = urlparse(repo_url)
        parts = parsed.path.strip("/").split("/")
        return parts[0], parts[1]
    except Exception:
        return None


def _fetch_readme(owner: str, repo: str) -> str | None:
    branches = ["main", "master"]
    filenames = ["README.md", "Readme.md", "readme.md"]

    headers = {
        "User-Agent": "resume-chatbot/1.0"
    }

    for branch in branches:
        for filename in filenames:
            url = f"{GITHUB_RAW_BASE}/{owner}/{repo}/{branch}/{filename}"
            try:
                resp = requests.get(url, timeout=REQUEST_TIMEOUT, headers=headers)
                if resp.status_code == 200 and resp.text.strip():
                    return resp.text.strip()
            except requests.RequestException:
                continue

    return None


def _fetch_project_repos(user_id: str) -> List[Dict]:
    """
    Lazy DB access (IMPORTANT)
    """

    # 🔥 lazy import
    from db.db import get_db_conn

    sql = """
        SELECT
            project_id,
            title,
            github_url
        FROM projects
        WHERE user_id = %s
          AND github_url IS NOT NULL
    """

    with get_db_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (user_id,))
            rows = cur.fetchall()

    return [
        {
            "project_id": r[0],
            "title": r[1],
            "github_url": r[2],
        }
        for r in rows
    ]


def fetch_github_knowledge(user_id: str) -> List[str]:
    """
    Build GitHub README knowledge chunks.
    """

    repos = _fetch_project_repos(user_id)
    chunks: List[str] = []

    for repo in repos:
        parsed = _parse_repo_owner_and_name(repo["github_url"])
        if not parsed:
            continue

        owner, repo_name = parsed
        readme = _fetch_readme(owner, repo_name)

        if not readme:
            continue

        max_chars = 6000
        if len(readme) > max_chars:
            readme = readme[:max_chars] + "\n\n[TRUNCATED]"

        chunk = f"""
GITHUB PROJECT README
Project Title: {repo['title']}
Repository: {repo['github_url']}

README CONTENT:
{readme}
""".strip()

        chunks.append(chunk)

    return chunks