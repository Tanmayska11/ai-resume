
import streamlit.components.v1 as components
from db.queries.skills import fetch_skills


def render_skills():
    skills = fetch_skills(limit=8)   # keep it tight

    components.html(
        f"""
        <style>
        .skill-card {{
            background: #f9fafb;
            border-radius: 16px;
            padding: 1.4rem 1.6rem;
            box-shadow: 0 10px 26px rgba(0,0,0,0.08);
            border-left: 4px solid #1f2937;
            font-family: system-ui;
        }}

        .skill-item {{
            margin-bottom: 0.8rem;
        }}

        .skill-name {{
            font-size: 0.8rem;
            margin-bottom: 0.25rem;
            color: #111827;
        }}

        .skill-bar {{
            height: 6px;
            background: #e5e7eb;
            border-radius: 6px;
            overflow: hidden;
        }}

        .skill-fill {{
            height: 100%;
            background: #2563eb;
        }}
        </style>

        <div class="skill-card">
            <h4>Skills</h4>

            {"".join([
                f'''
                <div class="skill-item">
                    <div class="skill-name">{s["name"]}</div>
                    <div class="skill-bar">
                        <div class="skill-fill" style="width:{s["level"]}%"></div>
                    </div>
                </div>
                '''
                for s in skills
            ])}
        </div>
        """,
        height=360,
        scrolling=True
    )