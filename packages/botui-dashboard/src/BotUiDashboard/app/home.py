import os
import streamlit as st


from BotUiDashboard.app.api_client import kill_bot_api, get_active_workers, get_outputs, start_bot_api

st.set_page_config(layout="wide", page_title="BotUI Stress Control")
BOTUI_WORKER_NAME = os.getenv("BOTUI_WORKER_NAME", "botui_worker")

@st.dialog("Real-Time Monitoring", width="large")
def show_bot_details(job_id):
    st.markdown("<style>div[role='dialog'] {max-width: 95vw !important; width: 95vw !important;}</style>", unsafe_allow_html=True)
    
    @st.fragment(run_every=1)
    def dialog_content():
        exists, screenshot, logs, _ = get_outputs(job_id)
        if not exists:
            st.error("Container not found.")
            return
        
        col_log, col_img = st.columns([1, 1])
        with col_log:
            st.caption("Console Logs")
            st.code(logs if logs else "Waiting...", height=600)
        with col_img:
            st.caption("Last Screenshot")
            if screenshot: st.image(screenshot, use_container_width=True)
            else: st.warning("No screenshots yet.")

    st.write(f"Inspecting: **{job_id}**")
    dialog_content()

@st.dialog("New Bot", width="large")
def new_bot_dialog():
    col1, col2 = st.columns([3, 1])
    with col1:
        pipeline_dir = st.text_input("Pipeline Directory", value="/Users/gabrielluciano/Desktop/coding/pessoal/BotUiYaml/_teste")
        bot_yaml_path = st.text_input("Bot YAML", value="bot_yaml.yaml")
        var_yaml_path = st.text_input("Variables YAML", value="bot_variables.yaml")
    
    with col2:
        n = st.number_input("Numero de Bots Para criar", value=1, min_value=1, max_value= 10)

    if st.button("Start Execution", use_container_width=True, type="primary"):
        payload = {
            "pipeline_dir": pipeline_dir,
            "bot_relative_path": bot_yaml_path, 
            "globals_relative_path": var_yaml_path,
            "n_instances": int(n)
        }
        try:
            res = start_bot_api(payload)
            if res.status_code == 200: st.rerun()
            else: st.error(f"Error: {res.text}")
        except Exception as e: st.error(f"API Failure: {e}")


st.subheader("Bots Control Panel")

all_bots = get_active_workers()
c_status, c_del, c_new = st.columns([4, 1, 1])

with c_status:
    count = len(all_bots)
    running = sum(1 for b in all_bots if b['state'] == 'running')
    st.write(f"Total: **{count}** | Running: **{running}**")

with c_del:
    if all_bots and st.button("Delete All", key="btn_del_all", use_container_width=True, type="primary"):
        for b in all_bots:
            kill_bot_api(b["name"].replace(f"{BOTUI_WORKER_NAME}_", ""))
        st.rerun()

with c_new:
    if st.button("New Bot", key="btn_new_bot", use_container_width=True):
        new_bot_dialog()

st.divider()

@st.fragment(run_every=2)
def render_table_rows():
    bots_streaming = get_active_workers()
    
    h1, h2, h3, h4 = st.columns([3, 1, 1, 1])
    h1.write("**Bot Name**")
    h2.write("**Status**")
    h3.write("**Analysis**")
    h4.write("**Action**")
    st.divider()

    if not bots_streaming:
        st.info("No active workers.")
        return

    for bot in bots_streaming:
        row_c1, row_c2, row_c3, row_c4 = st.columns([3, 1, 1, 1])
        jid = bot["name"].replace(f"{BOTUI_WORKER_NAME}_", "")

        row_c1.code(bot["name"], language=None)
        state = bot["state"]
        exit_code = bot["exit_code"]

        if state == "running":
            color = "green"
        elif state == "exited":
            color = "green" if exit_code == 0 else "red"
        else:
            color = "gray"

        row_c2.markdown(f":{color}[{bot['status']}]")
        
        if row_c3.button("Check", key=f"check_{bot['id']}", use_container_width=True):
            show_bot_details(jid)

        if row_c4.button("Delete", key=f"del_{bot['id']}", use_container_width=True):
            kill_bot_api(jid)
            st.rerun() 

render_table_rows()