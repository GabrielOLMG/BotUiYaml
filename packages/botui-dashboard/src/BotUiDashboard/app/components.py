import streamlit as st
import requests

# URL base da API (centralizada para facilitar manutenção)
API_BASE_URL = "http://botui_api:8000"

def inject_custom_css(log_height):
    """Injeta o CSS para estilizar a caixa de logs."""
    st.markdown(f"""
        <style>
        .log-container {{
            background-color: #1e1e1e;
            color: #d4d4d4;
            padding: 10px;
            border-radius: 5px;
            height: {log_height}px;
            overflow-y: scroll;
            font-family: monospace;
            font-size: 12px;
            white-space: pre-wrap;
        }}
        </style>
    """, unsafe_allow_html=True)

def inject_auto_scroll_js():
    """Injeta JavaScript para garantir que o log sempre role para baixo."""
    st.components.v1.html("""
        <script>
        const scroll=()=>{
            const l=window.parent.document.querySelectorAll('.log-container');
            l.forEach(el=>el.scrollTop=el.scrollHeight)
        };
        const obs=new MutationObserver(scroll);
        setInterval(()=>{
            const t=window.parent.document.querySelectorAll('.log-container');
            if(t.length>0){
                t.forEach(el=>obs.observe(el,{childList:true,subtree:true}))
            }
        },1000);
        </script>
    """, height=0)

@st.dialog("🔍 Visual Debug & OCR Toolkit", width="large")
def open_visual_debug_toolkit(pipeline_dir):
    """Abre a janela flutuante para testes de OCR e busca visual."""
    st.write(f"**Pipeline Ativo:** `{pipeline_dir}`")
    st.write("Configure os parâmetros para testar o reconhecimento visual no projeto.")
    
    # --- FORMULÁRIO DE DEBUG ---
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            img_path = st.text_input(
                "Caminho da Imagem (image_path)", 
                value="outputs/screenshots/last_screenshot.png",
                help="Caminho relativo à raiz do seu pipeline"
            )
            text_target = st.text_input(
                "Texto Alvo (text_target)", 
                placeholder="Ex: Login, Confirmar, Salvar..."
            )
        
        with col2:
            st.caption("Área de Busca (search_area)")
            g_row1, g_row2 = st.columns(2)
            row = g_row1.number_input("Linha (row)", min_value=0, value=0)
            column = g_row2.number_input("Coluna (column)", min_value=0, value=0)
            grid_rows = g_row1.number_input("Grid Rows", min_value=1, value=3)
            grid_cols = g_row2.number_input("Grid Cols", min_value=1, value=3)

    # --- EXECUÇÃO ---
    if st.button("🔬 Analisar Imagem", use_container_width=True, type="primary"):
        # Montagem do payload conforme sua especificação
        payload = {
            "image_path": img_path,
            "text_target": text_target,
            "search_area": {
                "row": row,
                "column": column,
                "grid_rows": grid_rows,
                "grid_cols": grid_cols
            }
        }
        
        with st.spinner("Processando OCR..."):
            try:
                # Faz a chamada para o endpoint de debug
                response = requests.post(
                    f"{API_BASE_URL}/debug/ocr", 
                    json=payload, 
                    timeout=15
                )
                
                if response.status_code == 200:
                    st.success("Análise finalizada com sucesso!")
                    # Aqui você pode exibir o JSON de retorno ou a imagem processada
                    st.json(response.json())
                else:
                    st.error(f"Erro na API ({response.status_code}): {response.text}")
                    
            except Exception as e:
                st.error(f"Falha na comunicação com a API: {str(e)}")

    st.divider()
    
    # Placeholder para visualização futura do Canvas de Debug
    debug_canvas = st.empty()
    debug_canvas.info("O resultado visual (imagem com marcações) aparecerá aqui.")