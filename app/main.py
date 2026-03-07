#app/main.py


import streamlit as st

# Import page renderers
from app._pages.dashboard import render_dashboard
from dotenv import load_dotenv

load_dotenv() 


def main():
    # ---------- App config ----------
    st.set_page_config(
        page_title="Tanmay Khairnar | Interactive Resume",
        layout="wide"
    )

    # ---------- Load resume (single source of truth) ----------
    # try:
    #     #resume = load_resume()
    #     resume= None
    # except Exception as e:
    #     st.error("Failed to load resume data.")
    #     st.exception(e)
    #     st.stop()

    # ---------- Routing ----------
    query_params = st.query_params
    page = query_params.get("page", "dashboard")

    
    # # ---------- Header (global) Portfolio Highlight (HR-first) ----------
    # render_header() 

    # render_action_buttons()


    st.divider()

    # ---------- Route handling ----------
    
    render_dashboard()



if __name__ == "__main__":
    main()
