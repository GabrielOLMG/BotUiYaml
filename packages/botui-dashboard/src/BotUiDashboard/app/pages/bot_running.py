import streamlit as st

st.write("Esta é a página de teste.")

if st.button("Voltar para Home"):
    st.switch_page("home.py") # Atalho para navegar via código