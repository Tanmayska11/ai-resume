import streamlit as st
import streamlit.components.v1 as components
from app.components.profile import render_profile
from app.components.experience import render_experience
from app.components.timeline import render_career_timeline
from app.components.education import render_education
from app.components.skills import render_skills
from app.components.projects import render_projects
from app.components.interests import render_interests
from app.components.interests import render_languages
from app.components.header import render_action_buttons
from app.components.header import render_header





def render_dashboard():

    render_header() 

    render_action_buttons()
   
    # ---- Layout ----
    left, right = st.columns([1.2, 2.8], gap="large")
    
    # =========================
    # LEFT PROFILE PANEL
    # =========================
    with left:
        render_profile()
        

    # =========================
    # RIGHT MAIN CONTENT
    # =========================
    with right:
       
        # ---- EXPERIENCE ----

        render_experience()

        # ---- TIMELINE ----

        render_career_timeline()      

        edu_col, skills_col, proj_col = st.columns(3, gap="small") 

        with edu_col:
             # ---- EDUCATION ----
            render_education()

        with skills_col:
             # ---- skills ----
            render_skills()

        with proj_col:
             # ---- projects ----
            render_projects()

        interests_col, lang_col = st.columns(2, gap="medium")

        with interests_col:
            render_interests()

        with lang_col:
            render_languages()
    











