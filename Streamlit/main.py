import streamlit as st
from user_agents import parse

import os

st.write("Archivos en Streamlit/pages/:")
st.write(os.listdir("Streamlit/pages/"))

# Obtener el User-Agent correctamente con la nueva API
query_params = st.query_params
user_agent = query_params.get("user-agent", [""])[0] if query_params else ""

ua = parse(user_agent)

# Detectar si es móvil o escritorio
is_mobile = ua.is_mobile

# Redirigir a la página correspondiente dentro de `pages/`
if is_mobile:
    st.switch_page("Mobile")  # Redirige a Mobile.py dentro de /pages
else:
    st.switch_page("Desktop")  # Redirige a Desktop.py dentro de /pages
