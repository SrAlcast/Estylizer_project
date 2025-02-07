import streamlit as st

st.set_page_config(page_title="Selector de versión", layout="centered")

st.title("Bienvenido a la plataforma de streaming")
st.write("Selecciona la versión que deseas utilizar:")

col1, col2 = st.columns(2)

with col1:
    if st.button("Versión Móvil 📱"):
        st.page_link("pages/mobile.py")

with col2:
    if st.button("Versión Escritorio 🖥️"):
        st.page_link("pages/desktop.py")
