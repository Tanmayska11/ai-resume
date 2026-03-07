import streamlit.components.v1 as components
from db.queries.experience import fetch_professional_experience





def render_experience():
    exp_list = fetch_professional_experience()

    components.html(
        f"""
        <style>
        .exp-wrapper {{
            font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        .exp-card {{
            background: #f9fafb;                    /* soft off-white */
            border-radius: 16px;
            padding: 5px 1.8rem;
            box-shadow: 0 10px 26px rgba(0,0,0,0.08);
            border-left: 4px solid #1f2937;          /* subtle anchor */
        }}


        .exp-title {{
            font-size: 1.05rem;
            font-weight: 600;
            color: #1f2d3a;
        }}

        .exp-meta {{
            font-size: 0.85rem;
            color: #6b7280;
            margin-top: 0.25rem;
        }}

        .exp-desc {{
            margin-top: 0.9rem;
            line-height: 1.55;
            color: #374151;
        }}
   
              
        </style>

        <div class="exp-wrapper">
           

            {"".join([
                f'''
                <div class="exp-card">
                    <h3>Experience</h3>
                    <div class="exp-title">{e["role"]} — {e["company"]}</div>
                    <div class="exp-meta">{e["location"]} | {e["duration"]}</div>
                    <div class="exp-desc">{e["context"]}</div>
                </div>
                '''
                for e in exp_list
            ])}
        </div>
        """,
        height=170,    #experience and timeline gap 50

        scrolling=False
    )
