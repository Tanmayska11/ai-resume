
import streamlit.components.v1 as components
from db.queries.projects import fetch_projects



def render_projects():
    projects = fetch_projects(limit=4)

    components.html(
        f"""
        <style>
        .proj-card {{
            background: #f9fafb;
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            box-shadow: 0 10px 26px rgba(0,0,0,0.08);
            border-left: 4px solid #1f2937;
            font-family: system-ui;
        }}

        .proj-item {{
            margin-bottom: 0.9rem;
        }}

        .proj-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: #111827;
        }}

        .proj-link {{
            font-size: 0.75rem;
            color: #2563eb;
            text-decoration: none;
        }}
        </style>

        <div class="proj-card">
            <h4>Projects</h4>

            {"".join([
                f'''
                <div class="proj-item">
                    <div class="proj-title">{p["title"]}</div>
                    <a class="proj-link" href="{p["github"]}" target="_blank">
                        GitHub ↗
                    </a>
                </div>
                '''
                for p in projects
            ])}
        </div>
        """,
        height=360,
        scrolling=False
    )



