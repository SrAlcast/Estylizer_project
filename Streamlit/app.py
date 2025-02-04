import streamlit as st

# Inyectar JavaScript para obtener el tamaño de la pantalla
screen_width = st.session_state.get("screen_width", 800)  # Valor por defecto
screen_js = """
<script>
    function sendScreenSize() {
        var width = window.innerWidth;
        var streamlitSendMessage = window.parent.postMessage;
        streamlitSendMessage({'screen_width': width}, '*');
    }
    window.onload = sendScreenSize;
    window.onresize = sendScreenSize;
</script>
"""

st.components.v1.html(screen_js, height=0)

# Capturar el mensaje desde JavaScript
if "screen_width" not in st.session_state:
    st.session_state["screen_width"] = 800  # Valor por defecto

def on_message(msg):
    if "screen_width" in msg:
        st.session_state["screen_width"] = msg["screen_width"]

st.session_state["screen_width"] = st.experimental_get_query_params().get("screen_width", [800])[0]

# Definir umbral para considerar móvil o escritorio
MOBILE_WIDTH_THRESHOLD = 768  # Ajusta este valor según tus necesidades

if st.session_state["screen_width"] < MOBILE_WIDTH_THRESHOLD:
    st.switch_page("pages/Mobile")  # Redirigir a la página de móvil
else:
    st.switch_page("pages/Desktop")  # Redirigir a la página de escritorio

