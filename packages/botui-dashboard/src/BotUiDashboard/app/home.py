import streamlit as st
import hashlib
import time

from pathlib import Path

from BotUiDashboard.app.api_client import get_outputs, start_bot_api
from BotUiDashboard.app.components import inject_custom_css, inject_auto_scroll_js, open_ocr_toolkit, open_screenshot_history
from BotUiDashboard.app.state_manager import init_state

LOG_HEIGHT = 250
SCREENSHOT_WIDTH = 500
REFRESH_RATE = 0.3
MAX_SCREENSHOTS = 100

st.set_page_config(page_title="BotUi Control Center", layout="wide")

init_state()

inject_custom_css(LOG_HEIGHT)

with st.sidebar:
    st.title("BotUi")
    
    with st.expander("Path Settings", expanded=True):
        pipeline_dir = st.text_input(
            "Pipeline Directory", 
            value="/Users/gabrielluciano/Desktop/coding/pessoal/BotUiYaml/_teste"
        )
        bot_path = st.text_input("Bot YAML", value="bot_yaml.yaml")
        vars_path = st.text_input("Variables YAML", value="bot_variables.yaml")
        debug_mode = st.checkbox("Bot Internal Debug", value=False)
    
    st.divider()

    st.subheader("Bot Control")
    if not st.session_state.get("bot_running"):
        if st.button("Start Execution", use_container_width=True, type="primary"):
            payload = {
                "pipeline_dir": pipeline_dir,
                "bot_relative_path": bot_path,
                "globals_relative_path": vars_path,
                "debug": debug_mode
            }
            try:
                res = start_bot_api(payload)
                if res.status_code == 200:
                    st.session_state.last_container_id = res.json().get("container_id")
                    st.session_state.pipeline_name = res.json().get("pipeline_name")

                    st.session_state.bot_running = True
                    st.rerun()
                else:
                    st.error(f"Start error: {res.text}")
            except Exception as e:
                st.error(f"API Failure: {e}")
    else:
        if st.button("Stop Visual Monitoring", use_container_width=True):
            st.session_state.bot_running = False
            st.rerun()
    
    st.divider()
    
    st.subheader("Tools")
    if st.button("OCR Toolkit", use_container_width=True):
        open_ocr_toolkit(pipeline_dir)
    
    if st.button("View screenshot history", use_container_width=True):
        open_screenshot_history()

st.header("Execution Dashboard")

canvas_placeholder = st.empty()
st.divider()
st.subheader("Execution Logs")
log_placeholder = st.empty()

inject_auto_scroll_js()
pipeline_status_placeholder = st.empty()

if st.session_state.get("bot_running"):
    container_id = st.session_state.get("last_container_id")
    pipeline_name = st.session_state.get("pipeline_name")

    while st.session_state.bot_running:
        exists, screenshot, logs = get_outputs(container_id, pipeline_name)

        if not exists:
            st.session_state.bot_running = False
            st.rerun()

        if screenshot:
            current_hash = hashlib.md5(screenshot).hexdigest()
            last_hash = st.session_state.get("last_screenshot_hash")
            if current_hash != last_hash:
                st.session_state.screenshot_history.append(screenshot)
                st.session_state.last_screenshot_hash = current_hash
                
                if len(st.session_state.screenshot_history) > MAX_SCREENSHOTS:
                    st.session_state.screenshot_history.pop(0)

            try:
                canvas_placeholder.image(screenshot, width=SCREENSHOT_WIDTH, use_container_width=True)
            except Exception as e:
                print(f"Placeholder error: {e}")
        
        if not logs:
            logs = st.session_state.last_log 
        else: 
            st.session_state.last_log = logs

        log_placeholder.markdown(
            f'<div class="log-container">{logs}</div>', 
            unsafe_allow_html=True
        )
        
        time.sleep(REFRESH_RATE)
        if not st.session_state.bot_running:
            break
else:
    canvas_placeholder.info("Waiting for bot to start monitoring...")
    if st.session_state.last_log:
        log_placeholder.markdown(
            f'<div class="log-container">{st.session_state.last_log}</div>', 
            unsafe_allow_html=True
        )
    else:
        log_placeholder.markdown(
            '<div class="log-container">Waiting for execution logs...</div>', 
            unsafe_allow_html=True
        )

    if st.session_state.screenshot_history:
        canvas_placeholder.image(st.session_state.screenshot_history[-1], width=SCREENSHOT_WIDTH, use_container_width=True)