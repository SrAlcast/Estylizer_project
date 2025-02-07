import streamlit as st

st.set_page_config(page_title="Selector de versión", layout="centered")

# Imagen logo superior
st.markdown(f"""
<div class='image-container' style="margin-top: 15px; margin-bottom: 20px;">
    <img src="https://raw.githubusercontent.com/SrAlcast/Estylizer_project/refs/heads/main/src/Logo_Estylizer_2.png" style="max-width: 200px;">
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/desktop.py")
    
with col2:
    st.page_link("pages/Mobile.py")
