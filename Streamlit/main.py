import streamlit as st
import locale
locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')


st.set_page_config(page_title="Selector de versión", layout="centered")

st.markdown(
    """
    <style>
    .stButton > button {
        width: 350px !important;
        height: 70px !important;
        border-radius: 15px !important;
        font-size: 22px !important;
        font-weight: bold;
        display: block;
        margin: 10px auto !important;
    }
    .centered-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        flex-direction: column;
        gap: 20px;
        margin-top: 30px;
    }
    .image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
    }
    .image-container img {
        max-width: 100%;
        height: auto;
        border-radius: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Imagen logo superior
st.markdown(f"""
<div class='image-container' style="margin-top: 15px; margin-bottom: 20px;">
    <img src="https://raw.githubusercontent.com/SrAlcast/Estylizer_project/refs/heads/main/src/Logo_Estylizer_2.png" style="max-width: 200px;">
</div>
""", unsafe_allow_html=True)

# Contenedor para centrar los botones
st.markdown("<div class='centered-container'>", unsafe_allow_html=True)

st.page_link("pages/desktop.py", label="Versión Desktop")
st.page_link("pages/Mobile.py", label="Versión Mobile")

st.markdown("</div>", unsafe_allow_html=True)
