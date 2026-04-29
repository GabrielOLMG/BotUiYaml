import streamlit as st

def init_state():
    if "bot_running" not in st.session_state:
        st.session_state.bot_running = False
    if "last_job_id" not in st.session_state:
        st.session_state.last_job_id = None