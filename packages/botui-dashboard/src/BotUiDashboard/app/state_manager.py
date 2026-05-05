import streamlit as st

def init_state():
    if "bot_running" not in st.session_state:
        st.session_state.bot_running = False
    if "last_job_id" not in st.session_state:
        st.session_state.last_job_id = None
    if "job_id" not in st.session_state:
        st.session_state.job_id = None
    if "pipeline_name" not in st.session_state:
        st.session_state.pipeline_name = None
    if "screenshot_history" not in st.session_state:
        st.session_state.screenshot_history = []
    if "last_log" not in st.session_state:
        st.session_state.last_log = None
    if "last_screenshot_hash" not in st.session_state:
        st.session_state.last_screenshot_hash = None