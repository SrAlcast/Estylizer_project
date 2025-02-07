import streamlit as st

st.set_page_config(page_title="Selector de versión", layout="centered")

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem !important;
        margin: auto;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-size: 16px;
    }
    .title-text {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
        color: #ff5733;
    }
    .centered-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        flex-direction: column;
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
    .centered-title {
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        font-size: 22px;
        font-weight: bold;
        color: white;
    }
    .divider {
        width: 50%;
        margin: auto;
        border: 1px solid red; /* Línea muy fina */
    }
    .centered {
        text-align: center;
    }
    .coste-total {
        display: flex;
        justify-content: center;
        align-items: center;
        text-align: center;
        font-size: 18px;
        font-weight: bold;
        color: white;
        margin-top: 5px;
        margin-bottom: 5px;
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

col1, col2 = st.columns(2)

with col1:
    st.page_link("pages/desktop.py")

with col2:
    st.page_link("pages/Mobile.py")
