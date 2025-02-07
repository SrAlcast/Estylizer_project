import streamlit as st

st.set_page_config(page_title="Selector de versión", layout="centered")

st.title("Bienvenido a la plataforma de streaming")
st.write("Selecciona la versión que deseas utilizar:")

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/desktop.py")
with col2:
    st.page_link("pages/mobile.py")
