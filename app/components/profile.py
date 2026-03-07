import streamlit.components.v1 as components
from app.utils.assets import image_to_base64
from db.queries.profile import fetch_profile
import base64
from pathlib import Path


def image_to_base64(relative_path: str) -> str:
    image_path = Path(relative_path)
    return base64.b64encode(image_path.read_bytes()).decode()

def render_profile():
    profile = fetch_profile()
    profile_photo = image_to_base64(
        "assets/images/profile_photo.jpeg"
    )
    components.html(


            f"""
            <!-- ========================= -->
            <!-- IFRAME BASE RESET -->
            <!-- Ensures full width usage -->
            <!-- ========================= -->
            <style>
            html, body {{
                width: 100%;
                margin: 0;
                padding: 0;
            }}

            /* ========================= */
            /* MAIN PROFILE CONTAINER */
            /* ========================= */
            .profile-panel {{
                width: 100%;                 /* full column width */
                box-sizing: border-box;
                background: linear-gradient(
                    180deg, #2c3e50, #1f2d3a
                );
                color: #ffffff;
                padding: 1.8rem 1.6rem;
                border-radius: 16px;

                /* layout */
                display: flex;
                flex-direction: column;           /* vertical stacking */
                gap: 1.2rem;                      /* space between sections */

                /* typography */
                font-family: system-ui, -apple-system,
                            BlinkMacSystemFont, sans-serif;
            }}

            /* ========================= */
            /* HEADER: PHOTO + NAME */
            /* ========================= */

            .profile-photo-wrapper {{
                display: flex;
                justify-content: center;
            }}

            .profile-header {{
                display: flex;
                justify-content: center;
            }}

            .profile-header-content {{
                display: flex;
                flex-direction: column;
                align-items: center;      /* THIS is the key */
                text-align: center;       /* centers text properly */
            }}

         

            .profile-photo {{
                
                width: 150px;                       /* adjust image size here */
                height: 150px;
                border-radius: 50%;
                object-fit: cover;
                border: 2px solid rgba(255,255,255,0.35);
                flex-shrink: 0;                    /* prevents image compression */
            }}

            .profile-name {{
                font-size: 1.55rem;                /* name size */
                font-weight: 700;
                line-height: 1.2;
            }}

            .profile-role {{
                font-size: 0.9rem;                 /* role size */
                opacity: 0.85;
                margin-top: 0.15rem;
            }}

            /* ========================= */
            /* SUMMARY / ABOUT SECTION */
            /* ========================= */
            .profile-summary {{
                width: 100%;
                font-size: 0.9rem;
                line-height: 1.55;
                opacity: 0.95;

                /* summary spacing */
                margin-top: 0.2rem;
            }}

            /* ========================= */
            /* CONTACT DETAILS */
            /* ========================= */
            .profile-contact {{
                display: flex;
                flex-direction: column;
                gap: 0.65rem;                      /* spacing between contact rows */
                font-size: 0.88rem;
            }}

            .profile-contact a {{
                color: #9fd3ff;                    /* link color */
                text-decoration: none;
            }}

            /* ========================= */
            /* SEPARATOR LINES */
            /* ========================= */

            .profile-divider {{
                width: 42px;             /* short elegant line */
                height: 2px;
                background: rgba(255,255,255,0.95);
                margin-top: 0.35rem;
                margin-bottom: 0.75rem;
            }}

            /* summary left accent */
            .profile-summary-wrapper {{
                border-left: 2px solid rgba(255,255,255,0.75);
                padding-left: 0.9rem;
            }}

            /* summary bottom divider */
            .profile-summary-end {{
                width: 100%;
                height: 1.5px;
                background: rgba(255,255,255,0.6);
                margin-top: 1rem;
            }}

            /* ========================= */
            /* SECTION HEADINGS */
            /* ========================= */

            .profile-section-title {{
                font-size: 18px;          /* clearly smaller than name */
                font-weight: 600;
                letter-spacing: 0.06em;
                text-transform: uppercase;
                opacity: 1;
                margin-bottom: 0.4rem;
            }}

            </style>

            <!-- ========================= -->
            <!-- PROFILE PANEL CONTENT -->
            <!-- ========================= -->
            <div class="profile-panel">

                <!-- Header -->
                <div class="profile-header">
                    <div class="profile-header-content">
                        <img src="data:image/jpeg;base64,{profile_photo}" class="profile-photo" />

                        
                        <br/><br/>
                        <div class="profile-name">{profile['name']}</div>
                        <div class="profile-divider"></div>
                        <div class="profile-role">{profile['title']}</div>
                    </div>
                </div>


                <!-- Summary -->
                <br/>
                <div class="profile-summary-wrapper">
                    <div class="profile-section-title">About Me</div>
                    <br/>
                    <div class="profile-summary">
                        {profile['summary']}
                    </div>
                    <br/>
                    <div class="profile-summary-end">
                    
                    </div>
                    
                </div>

                <!-- Contact -->
                <div class="profile-contact">
                    <div class="profile-section-title">Contact Me</div>
                    <div>📍 {profile['location']}</div>
                    <div>📧 {profile['contact']['email']}</div>
                    <div> 📞 {profile['contact']['phone']}</div>
                    <div>
                        🔗 <a href="{profile['contact']['linkedin']}" target="_blank">
                            LinkedIn
                        </a>
                    </div>
                </div>

            </div>
            """,
            height=1100,          # adjust if summary grows
            scrolling=False,
        )
