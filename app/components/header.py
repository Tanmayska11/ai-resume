 
import streamlit.components.v1 as components
import os
from dotenv import load_dotenv



load_dotenv()
FRONTEND_URL = os.getenv("NEXT_PUBLIC_FRONTEND_URL")

REACT_CHATBOT_URL = FRONTEND_URL
PREDICTION_URL = f"{FRONTEND_URL}/match"  # or React later

def render_header():
        components.html(
            """
            <style>
            .portfolio-highlight {
                background: rgba(20, 83, 45, 0.06);   /* very light green tint */
                border-radius: 16px;
                padding: 1.4rem 1.8rem;
                margin-bottom: 1.8rem;
                border-left: 4px solid #14532d;       /* deep green anchor */
                font-family: system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
            }

            .portfolio-highlight h2 {
                margin: 0 0 0.6rem 0;
                font-size: 1.25rem;
                font-weight: 600;
                color: #14532d;                       /* deep professional green */
            }

            .portfolio-highlight ul {
                margin: 0.6rem 0 0 1rem;
                padding: 0;
            }

            .portfolio-highlight li {
                margin-bottom: 0.5rem;
                color: #1f2937;                      /* readable dark text */
                line-height: 1.45;
            }

            .portfolio-highlight li::marker {
                color: #166534;                      /* slightly darker green bullet */
            }
            .title {
                text-align: center;
                font-size: 17px;
            }
            /* ===== Mobile adjustments ===== */
            @media (max-width: 640px) {

                .title h2 {
                    font-size: 1rem;        /* smaller title */
                    line-height: 1.4;
                    padding: 0 0.5rem;
                }

                .portfolio-highlight {
                    margin-left: 0.5rem;
                    margin-right: 0.5rem;   /* tighter padding */
                }

                .portfolio-highlight h2 {
                    font-size: 1.05rem;
                }

                .portfolio-highlight li {
                    font-size: 0.9rem;
                    line-height: 1.45;
                }
            }
            </style>
            <div class="title">
                <h2>A Production-style Resume System Combining Data Pipelines, Analytics & Applied Machine Learning.</h2>
            </div>

            <div class="portfolio-highlight">
                <h2>What this portfolio demonstrates</h2>
                <ul>
                    <li>Developed as a practical, end-to-end system.</li>
                    <li>Based on real data pipelines supporting analysis and prediction</li>
                    <li>Incorporates machine learning components used in live application flows</li>
                    <li>Includes an AI-assisted resume interface to support structured information access</li>
                </ul>
            </div>
            """,
            height=270,
            scrolling=False
        )




def render_action_buttons():
    components.html(
        f"""
        <style>
        .action-buttons {{
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-top: 1.2rem;
        }}

        .action-btn {{
            min-width: 220px;
            padding: 0.7rem 1.1rem;
            font-size: 0.85rem;
            font-weight: 600;
            border-radius: 10px;
            text-decoration: none;
            text-align: center;
            font-family: system-ui;
            cursor: pointer;
        }}

        .btn-chat {{
            background: #16a34a;
            color: white;
        }}

        .btn-predict {{
            background: #2563eb;
            color: white;
        }}
        </style>

        <div class="action-buttons">
            <a
                href="{REACT_CHATBOT_URL}"
                target="_blank"
                class="action-btn btn-chat"
            >
                💬 Open Resume Chatbot
            </a>

            <a
                href="{PREDICTION_URL}"
                target="_blank"
                class="action-btn btn-predict"
            >
                📊 View Career Prediction
            </a>
        </div>
        """,
        height=70,
        scrolling=False,
    )
