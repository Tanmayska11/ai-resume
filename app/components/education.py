import streamlit.components.v1 as components
from app.utils.assets import image_to_base64
from db.queries.education import fetch_latest_education




def render_education():
    # pick ONLY master's (assumes first entry is master's – which matches your JSON)
    edu = fetch_latest_education()
    germany_map_base64 = image_to_base64(
        "assets/images/germany_map.png"
    )

    components.html(
        f"""
        <style>
        /* ================= EDUCATION CARD ================= */

       .edu-card {{
            background: #f9fafb;
            border-radius: 16px;
            padding: 1.2rem 1.4rem;     /* ↓ reduced padding */
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            border-left: 4px solid #1f2937;
            margin-bottom: 1.4rem;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        /* === VERTICAL STACK === */
        .edu-column {{
            display: flex;
            flex-direction: column;
            align-items: flex-start;
            gap: 0.75rem;
        }}

        /* Smaller map */
        .edu-map img {{
            width: 95px;               /* ↓ reduced size */
            opacity: 0.9;
        }}

        /* Text */
        .edu-title {{
            font-size: 0.95rem;        /* ↓ smaller */
            font-weight: 600;
            color: #111827;
        }}

        .edu-meta {{
            font-size: 0.8rem;
            color: #4b5563;
        }}

        </style>

        <div class="edu-card">
            <h3>Education</h3>

            <div class="edu-column">

                <div class="edu-map">
                    <img src="data:image/png;base64,{germany_map_base64}">
                </div>

                <div class="edu-title">
                    {edu["degree"]}
                </div>

                <div class="edu-meta">
                    {edu["institution"]}
                </div>

                <div class="edu-meta">
                    {edu["location"]} | {edu["duration"]}
                </div>

            </div>

        </div>
        """,
        height=380,
        scrolling=False
    )
