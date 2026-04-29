import streamlit as st
import requests
import base64

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


@st.dialog("Visual Debug & OCR Toolkit", width="large")
def open_visual_debug_toolkit(pipeline_dir):
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            img_path = st.text_input("Caminho da Imagem", value="outputs/screenshots/last_screenshot.png")
            text_target = st.text_input("Texto Alvo", placeholder="Ex: Login")
        
        with col2:
            st.caption("Área de Busca (Deixe vazio para None)")
            g_row1, g_row2 = st.columns(2)
            
            # Usamos text_input para permitir que o campo fique vazio (None)
            r_val = g_row1.text_input("Row", value="", placeholder="None")
            c_val = g_row2.text_input("Column", value="", placeholder="None")
            gr_val = g_row1.text_input("Grid Rows", value=1, placeholder="None")
            gc_val = g_row2.text_input("Grid Cols", value=1, placeholder="None")

            # Função auxiliar interna para converter string vazia em None
            def to_int_or_none(val):
                try:
                    return int(val) if val.strip() != "" else None
                except ValueError:
                    return None

            search_area = {
                "row": to_int_or_none(r_val),
                "column": to_int_or_none(c_val),
                "grid_rows": to_int_or_none(gr_val),
                "grid_cols": to_int_or_none(gc_val)
            }

    debug_canvas = st.empty()

    if st.button("Analisar Imagem", use_container_width=True, type="primary"):
        # Removemos chaves que são None se você quiser um JSON limpo, 
        # ou enviamos o dicionário completo com nulls conforme sua API preferir.
        # Aqui, filtramos para enviar apenas o que foi preenchido:
        filtered_search_area = {k: v for k, v in search_area.items() if v is not None}
        
        # Se todos forem None, search_area vira None
        final_search_area = filtered_search_area if filtered_search_area else None

        payload = {
            "image_path": img_path,
            "text_target": text_target if text_target else None,
            "search_area": final_search_area
        }

        with st.spinner("Processando OCR..."):
            try:
                from api_client import API_BASE_URL 
                response = requests.post(f"{API_BASE_URL}/vision/ocr", json=payload, timeout=60)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("Análise finalizada!")
                    
                    with st.expander("Ver JSON de Retorno"):
                        st.json(data.get("result"))
                    
                    if data.get("debug_image"):
                        import base64
                        img_bytes = base64.b64decode(data["debug_image"])
                        debug_canvas.image(img_bytes, use_container_width=True)
                else:
                    st.error(f"Erro na API: {response.text}")
            except Exception as e:
                st.error(f"Erro: {str(e)}")