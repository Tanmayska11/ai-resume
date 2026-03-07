# chatbot/knowledge/github_ingestor.py

"""
Fetch and normalize GitHub README files
for chatbot grounding.

Source of truth:
- Repo URLs come from PostgreSQL
- Content is treated as READ-ONLY external knowledge
"""

import requests
from typing import List, Dict
from urllib.parse import urlparse

from db.db import get_db_conn


GITHUB_RAW_BASE = "https://raw.githubusercontent.com"
REQUEST_TIMEOUT = 10


def _parse_repo_owner_and_name(repo_url: str) -> tuple[str, str] | None:
    """
    Extract owner and repo name from GitHub URL.
    """
    try:
        parsed = urlparse(repo_url)
        parts = parsed.path.strip("/").split("/")
        return parts[0], parts[1]
    except Exception:
        return None


def _fetch_readme(owner: str, repo: str) -> str | None:
    """
    Fetch README.md from common branches and filenames.
    """

    branches = ["main", "master"]
    filenames = ["README.md", "Readme.md", "readme.md"]

    for branch in branches:
        for filename in filenames:
            url = f"{GITHUB_RAW_BASE}/{owner}/{repo}/{branch}/{filename}"
            try:
                resp = requests.get(url, timeout=REQUEST_TIMEOUT)
                if resp.status_code == 200 and resp.text.strip():
                    return resp.text.strip()
            except requests.RequestException:
                continue

    return None


def _fetch_project_repos(user_id: str) -> List[Dict]:
    """
    Fetch project_id, title, and repo URL from DB.
    """

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

        # --- truncate excessively long READMEs (token safety)
        max_chars = 6_000
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
