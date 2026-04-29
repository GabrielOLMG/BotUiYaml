import streamlit as st

def main():
    st.set_page_config(page_title="BotUi Teste", page_icon="🤖")

    st.title("Olá! Este é o Front-end do BotUi")
    st.write("Esta interface é um teste básico para visualizar como o Streamlit funciona.")

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Configurações de Texto")
        nome_bot = st.text_input("Nome do Bot", placeholder="Ex: OCR_Bot_01")
        descricao = st.text_area("Descrição da tarefa")

    with col2:
        st.subheader("Parâmetros Numéricos")
        tentativas = st.number_input("Número de tentativas", min_value=1, max_value=10, value=3)
        precisao = st.slider("Precisão do OCR", 0.0, 1.0, 0.8)

    st.divider()

    if st.button("Executar Teste"):
        st.success(f"O Bot '{nome_bot}' seria iniciado com {tentativas} tentativas!")
        st.balloons() # Um efeito visual apenas para comemorar

if __name__ == "__main__":
    main()