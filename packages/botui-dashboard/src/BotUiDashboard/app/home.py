import streamlit as st
import time
from BotUiDashboard.app.api_client import fetch_logs, fetch_screenshot, start_bot_api
from BotUiDashboard.app.components import inject_custom_css, inject_auto_scroll_js, open_visual_debug_toolkit
from BotUiDashboard.app.state_manager import init_state

# --- CONFIGURAÇÕES CONSTANTES ---
LOG_HEIGHT = 250
SCREENSHOT_WIDTH = 1000
REFRESH_RATE = 0.3

# --- SETUP DA PÁGINA ---
st.set_page_config(page_title="BotUi Control Center", layout="wide")

# Inicializa o estado global (bot_running, job_id, etc)
init_state()

# Injeta CSS personalizado para os Logs
inject_custom_css(LOG_HEIGHT)

# --- SIDEBAR: CONFIGURAÇÕES E CONTROLES ---
with st.sidebar:
    st.title("BotUi")
    
    with st.expander("Configurações de Caminho", expanded=True):
        pipeline_dir = st.text_input(
            "Pipeline Directory", 
            value="/Users/gabrielluciano/Desktop/coding/pessoal/BotUiYaml/_teste"
        )
        bot_path = st.text_input("Bot YAML", value="bot_yaml.yaml")
        vars_path = st.text_input("Variables YAML", value="bot_variables.yaml")
        debug_mode = st.checkbox("Bot Internal Debug", value=False)
    
    st.divider()

    st.subheader("Bot Control")
    # Alterna entre botão de Iniciar e Parar baseado no estado do bot
    if not st.session_state.get("bot_running"):
        if st.button("Iniciar Execução", use_container_width=True, type="primary"):
            payload = {
                "pipeline_dir": pipeline_dir,
                "bot_relative_path": bot_path,
                "globals_relative_path": vars_path,
                "debug": debug_mode
            }
            try:
                res = start_bot_api(payload)
                if res.status_code == 200:
                    st.session_state.last_job_id = res.json().get("job_id")
                    st.session_state.bot_running = True
                    st.rerun()
                else:
                    st.error(f"Erro ao iniciar: {res.text}")
            except Exception as e:
                st.error(f"Falha na API: {e}")
    else:
        if st.button("Parar Monitoramento Visual", use_container_width=True):
            st.session_state.bot_running = False
            st.rerun()
    
    st.divider()
    
    # Ferramenta de Debug que abre o Dialog (Toolkit OCR)
    st.subheader("Ferramentas")
    if st.button("Abrir Visual Debugger", use_container_width=True):
        open_visual_debug_toolkit(pipeline_dir)

# --- CONTEÚDO PRINCIPAL (DASHBOARD) ---
st.header("Dashboard de Execução")

# Placeholders para atualização dinâmica
canvas_placeholder = st.empty()
st.divider()
st.subheader("Logs de Execução")
log_placeholder = st.empty()

# Injeta o script de Auto-Scroll para os logs
inject_auto_scroll_js()

# --- LOOP DE ATUALIZAÇÃO EM TEMPO REAL ---
if st.session_state.get("bot_running"):
    job_id = st.session_state.get("last_job_id")
    
    # Loop de monitoramento enquanto o bot estiver "rodando" no front
    while st.session_state.bot_running:
        # 1. Atualiza Screenshot
        img = fetch_screenshot(job_id, pipeline_dir)
        if img:
            try:
                canvas_placeholder.image(img, width=SCREENSHOT_WIDTH)
            except:
                pass # Ignora frames corrompidos durante a escrita
        
        # 2. Atualiza Logs
        logs = fetch_logs(job_id)
        log_placeholder.markdown(
            f'<div class="log-container">{logs}</div>', 
            unsafe_allow_html=True
        )
        
        # Controle de frequência
        time.sleep(REFRESH_RATE)
else:
    # Estado ocioso
    canvas_placeholder.info("Aguardando início do bot para monitoramento...")
    log_placeholder.markdown(
        '<div class="log-container">Aguardando logs de execução...</div>', 
        unsafe_allow_html=True
    )