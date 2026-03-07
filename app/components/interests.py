import streamlit.components.v1 as components


def render_interests():
    components.html(
        """
        <style>
        .card {
            background: #f9fafb;
            border-radius: 16px;
            padding: 1.2rem 1.6rem;
            box-shadow: 0 10px 26px rgba(0,0,0,0.08);
            border-left: 4px solid #1f2937;
            font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
        }

        .card h4 {
            margin: 0 0 0.6rem 0;
            color: #111827;
        }

        .card ul {
            margin: 0.4rem 0 0 1.2rem;
            padding: 0;
            line-height: 1.6;
            color: #1f2937;
        }
        </style>

        <div class="card">
            <h4>Interests</h4>
            <ul>
                <li>Football and table tennis </li>
                <li>Volunteering for education of underprivileged children</li>
                <li>Exploring data-driven business and ML systems</li>
                <li>Reading about system design and emerging technologies</li>
            </ul>
        </div>
        """,
        height=290,
        scrolling=False
    )




def render_languages():
    components.html(
        """
        <style>
        .lang-card {
            background: #f9fafb;
            border-radius: 16px;
            padding: 1.2rem 1.6rem;
            box-shadow: 0 10px 26px rgba(0,0,0,0.08);
            border-left: 4px solid #1f2937;
            font-family: system-ui;
        }

        .lang-wrapper {
            display: flex;
            align-items: center;
            gap: 1.4rem;
        }

        .legend {
            display: flex;
            flex-direction: column;
            gap: 0.45rem;
            font-size: 0.8rem;
            color: #1f2937;
        }

        .legend-item {
            display: flex;
            align-items: center;
            gap: 0.45rem;
        }

        .legend-color {
            width: 10px;
            height: 10px;
            border-radius: 50%;
        }
        </style>

        <div class="lang-card">
            <h4>Languages</h4>

            <div class="lang-wrapper">

                <!-- SVG PIE -->
                <svg width="160" height="160" viewBox="0 0 36 36">
                    <!-- background -->
                    <circle
                        cx="18" cy="18" r="15.9"
                        fill="none"
                        stroke="#e5e7eb"
                        stroke-width="3.2"
                    />

                    <!-- English 40% -->
                    <circle
                        cx="18" cy="18" r="15.9"
                        fill="none"
                        stroke="#1f2937"
                        stroke-width="3.2"
                        stroke-dasharray="40 60"
                        stroke-dashoffset="25"
                    />

                    <!-- German 20% -->
                    <circle
                        cx="18" cy="18" r="15.9"
                        fill="none"
                        stroke="#14532d"
                        stroke-width="3.2"
                        stroke-dasharray="20 80"
                        stroke-dashoffset="-15"
                    />

                    <!-- Hindi 20% -->
                    <circle
                        cx="18" cy="18" r="15.9"
                        fill="none"
                        stroke="#9ca3af"
                        stroke-width="3.2"
                        stroke-dasharray="20 80"
                        stroke-dashoffset="-35"
                    />

                    <!-- Marathi 20% -->
                    <circle
                        cx="18" cy="18" r="15.9"
                        fill="none"
                        stroke="#6b7280"
                        stroke-width="3.2"
                        stroke-dasharray="20 80"
                        stroke-dashoffset="-55"
                    />
                </svg>

                <!-- LEGEND -->
                <div class="legend">
                    <div class="legend-item">
                        <span class="legend-color" style="background:#1f2937"></span>
                        English
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background:#14532d"></span>
                        German
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background:#9ca3af"></span>
                        Hindi
                    </div>
                    <div class="legend-item">
                        <span class="legend-color" style="background:#6b7280"></span>
                        Marathi
                    </div>
                </div>

            </div>
        </div>
        """,
        height=270,
        scrolling=False,
    )
