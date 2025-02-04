import streamlit as st
from pathlib import Path
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random
import webbrowser
import sys
# Añadimos la carpeta que contiene nuestro .py al path de Python
sys.path.append("./src/")
import support_mongo as sm

st.set_page_config(page_title="Estylizer - Recomendaciones", layout="centered")

def recomendador_superior(productos, tags_aceptados_general, tags_aceptados_superior, tags_rechazados_general, tags_rechazados_superior, tipos_superior, colores_superior, presupuesto_superior_min, presupuesto_superior_max):
    
    # Unir los tags en una sola columna para cada producto
    productos['tags_combined'] = productos[['Tag_1','Tag_2','Tag_3']].fillna('').agg(' '.join, axis=1)
    
    # Vectorizar los tags de los productos
    vectorizer = CountVectorizer()
    tags_matrix = vectorizer.fit_transform(productos['tags_combined'])
    
    # Crear la cadena de tags del usuario aceptados
    tags_usuario_str = ' '.join(tags_aceptados_general + tags_aceptados_superior)
    user_vector = vectorizer.transform([tags_usuario_str])
    
    # Calcular similitud coseno
    similitudes = cosine_similarity(user_vector, tags_matrix).flatten()
    
    # Penalizar productos con tags rechazados
    penalizacion = productos['tags_combined'].str.contains('|'.join(tags_rechazados_general + tags_rechazados_superior), case=False, na=False).astype(int) * -0.1
    productos['similaridad'] = similitudes + penalizacion
    
    # Filtrar superiores (todo lo que no sea pantalón)
    superiores = productos[
        (~productos['Categoria'].str.contains('Pantalón', case=False, na=False)) &
        (productos['Categoria'].str.contains('|'.join(tipos_superior), case=False, na=False)) &
        (productos['color_homogeneizado'].isin(colores_superior)) &
        (productos['current_price'] >= presupuesto_superior_min) &
        (productos['current_price'] <= presupuesto_superior_max)
    ]
    
    # Ordenar los productos recomendados
    superiores = superiores.sort_values(by=['similaridad', 'current_price'], ascending=[False, True])
    
    return superiores

def recomendador_inferior(productos, tags_aceptados_general, tags_aceptados_inferior, tags_rechazados_general, tags_rechazados_inferior, colores_inferior, presupuesto_inferior_min, presupuesto_inferior_max):
    
    # Unir los tags en una sola columna para cada producto
    productos['tags_combined'] = productos[['Tag_1','Tag_2','Tag_3']].fillna('').agg(' '.join, axis=1)
    
    # Vectorizar los tags de los productos
    vectorizer = CountVectorizer()
    tags_matrix = vectorizer.fit_transform(productos['tags_combined'])
    
    # Crear la cadena de tags del usuario aceptados
    tags_usuario_str = ' '.join(tags_aceptados_general + tags_aceptados_inferior)
    user_vector = vectorizer.transform([tags_usuario_str])
    
    # Calcular similitud coseno
    similitudes = cosine_similarity(user_vector, tags_matrix).flatten()
    
    # Penalizar productos con tags rechazados
    penalizacion = productos['tags_combined'].str.contains('|'.join(tags_rechazados_general + tags_rechazados_inferior), case=False, na=False).astype(int) * -0.1
    productos['similaridad'] = similitudes + penalizacion
    
    # Filtrar inferiores (solo pantalones)
    inferiores = productos[
        (productos['Categoria'].str.contains('Pantalón', case=False, na=False)) &
        (productos['color_homogeneizado'].isin(colores_inferior)) &
        (productos['current_price'] >= presupuesto_inferior_min) &
        (productos['current_price'] <= presupuesto_inferior_max)
    ]
    
    # Ordenar los productos recomendados
    inferiores = inferiores.sort_values(by=['similaridad', 'current_price'], ascending=[False, True])
    
    return inferiores

@st.cache_data
def cargar_datos():
    bd = sm.conectar_a_mongo("PullnBearData")
    nombre_coleccion1 = "modelos_pull_hombre_pruebas"
    nombre_coleccion2 = "productos_pull_hombre_pruebas"
    modelos = sm.importar_a_dataframe(bd, nombre_coleccion1)
    productos = sm.importar_a_dataframe(bd, nombre_coleccion2)
    productos['current_price'] = pd.to_numeric(productos['current_price'], errors='coerce')
    return modelos, productos

modelos_tageados, productos_tageados = cargar_datos()

# Variables para el estado
if 'aceptados_general' not in st.session_state:
    st.session_state.aceptados_general = []
if 'rechazados_general' not in st.session_state:
    st.session_state.rechazados_general = []
if 'aceptados_superior' not in st.session_state:
    st.session_state.aceptados_superior = []
if 'rechazados_superior' not in st.session_state:
    st.session_state.rechazados_superior = []
if 'aceptados_inferior' not in st.session_state:
    st.session_state.aceptados_inferior = []
if 'rechazados_inferior' not in st.session_state:
    st.session_state.rechazados_inferior = []
if 'modelo_tags_index' not in st.session_state:
    st.session_state.modelo_tags_index = 0
if 'finalizado_modelo_tagss' not in st.session_state:
    st.session_state.finalizado_modelo_tagss = False
if 'random_indices' not in st.session_state:
    st.session_state.random_indices = random.sample(range(len(modelos_tageados)), 8)
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'tipos_superior' not in st.session_state:
    st.session_state.tipos_superior = []
if "select_all_colores_superior" not in st.session_state:
    st.session_state.select_all_colores_superior = False
if "select_all_colores_inferior" not in st.session_state:
    st.session_state.select_all_colores_inferior = False
if 'colores_superior' not in st.session_state:
    st.session_state.colores_superior = []
if 'colores_inferior' not in st.session_state:
    st.session_state.colores_inferior = []
if 'index_superior' not in st.session_state:
    st.session_state.index_superior = 0
if 'index_inferior' not in st.session_state:
    st.session_state.index_inferior = 0

# Función para resetear el estado
def resetear_estado():
    for key in st.session_state.keys():
        del st.session_state[key]


# CSS para centrar la imagen completamente
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
    </style>
    """,
    unsafe_allow_html=True,
)

# Mostrar logo centrado
st.markdown("<div class='centered-container'>", unsafe_allow_html=True)
st.image("./src/Logo Estylizer 2.png", width=200)
st.markdown("</div>", unsafe_allow_html=True)

# Página 1: Selección de modelo_tags
if st.session_state.page == 1:
    if st.session_state.modelo_tags_index < 8:
        modelo_tags = modelos_tageados.iloc[st.session_state.random_indices[st.session_state.modelo_tags_index]]

        # Forzar el centrado de la imagen con un contenedor flexbox
        st.markdown(f"""
        <div class='image-container'>
            <img src="{modelo_tags['image1_url']}" style="max-width: 260px;">
        </div>
        """, unsafe_allow_html=True)

        # Centrar los botones usando columnas
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            dislike_pressed = st.button("❌ No me gusta", key=f"dislike_{st.session_state.modelo_tags_index}")
            like_pressed = st.button("✅ Me gusta", key=f"like_{st.session_state.modelo_tags_index}")


        # Acciones de los botones con animación
        if dislike_pressed or like_pressed:
            if dislike_pressed:
                tags_rechazados_general = modelo_tags[['Tag_1', 'Tag_2']].values.flatten().tolist()
                tags_rechazados_superior = modelo_tags[['Tag_3', 'Tag_4']].values.flatten().tolist()
                tags_rechazados_inferior = modelo_tags[['Tag_5', 'Tag_6']].values.flatten().tolist()

                st.session_state.rechazados_general.append(tags_rechazados_general)
                st.session_state.rechazados_superior.append(tags_rechazados_superior)
                st.session_state.rechazados_inferior.append(tags_rechazados_inferior)

            if like_pressed:
                tags_aceptados_general = modelo_tags[['Tag_1', 'Tag_2']].values.flatten().tolist()
                tags_aceptados_superior = modelo_tags[['Tag_3', 'Tag_4']].values.flatten().tolist()
                tags_aceptados_inferior = modelo_tags[['Tag_5', 'Tag_6']].values.flatten().tolist()

                st.session_state.aceptados_general.append(tags_aceptados_general)
                st.session_state.aceptados_superior.append(tags_aceptados_superior)
                st.session_state.aceptados_inferior.append(tags_aceptados_inferior)

            st.session_state.modelo_tags_index += 1
            st.rerun()

        # Barra de progreso con numeración
        progreso = (st.session_state.modelo_tags_index + 1) / 8
        st.progress(progreso)
        st.write(f"Progreso: {st.session_state.modelo_tags_index + 1} de 8")

        # Inicializar estado si no existe
        if "confirm_reset" not in st.session_state:
            st.session_state.confirm_reset = False

        # Botón para solicitar confirmación
        if st.button("🔄 Resetear todo"):
            st.session_state.confirm_reset = True

        # Mostrar advertencia solo si el usuario ha presionado el botón
        if st.session_state.confirm_reset:
            st.warning("⚠️ ¿Seguro que quieres reiniciar el proceso?")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("✅ Sí, resetear"):
                    st.session_state.confirm_reset = False  # Resetear el estado de confirmación
                    resetear_estado()  # Llamar la función de reseteo
                    st.rerun()
            
            with col2:
                if st.button("❌ No, cancelar"):
                    st.session_state.confirm_reset = False  # Cancelar la acción
    else:
        st.success("¡Has terminado de seleccionar estilos!")
        st.session_state.page = 2
        st.rerun()


# Página 2: Selección de tipo de parte superior
if st.session_state.page == 2:
    st.subheader("¿Qué tipo de prenda quieres para la parte superior? (Selecciona múltiples opciones)")
    tipos = ["Camiseta", "Camisa", "Sudadera", "Jersey", "Polo", "Sobrecamisa"]
    

    if "select_all" not in st.session_state:
        st.session_state.select_all = False

    if "tipos_superior" not in st.session_state:
        st.session_state.tipos_superior = []

    def toggle_select_all():
        if st.session_state.select_all:
            st.session_state.tipos_superior = tipos.copy()
        else:
            st.session_state.tipos_superior = []

    # Botón "Seleccionar Todo"
    if st.button("Seleccionar Todo" if not st.session_state.select_all else "Deseleccionar Todo"):
        st.session_state.select_all = not st.session_state.select_all
        toggle_select_all()
        st.rerun()

    # Crear un desplegable multiselección
    seleccionados = st.multiselect(
        "Elige los tipos de prenda:",
        options=tipos,
        default=st.session_state.tipos_superior
    )

    # Guardar la selección en session_state
    st.session_state.tipos_superior = seleccionados

    # Botones de navegación
    nav_col1, nav_col2 = st.columns([1.5, 1.5])
    with nav_col1:
        if st.button("Siguiente"):
            if st.session_state.tipos_superior:
                st.session_state.page = 3
                st.rerun()
            else:
                st.warning("Por favor, selecciona al menos un tipo de prenda.")

    with nav_col2:
        if st.button("Volver"):
            resetear_estado()
            st.session_state.page = 1
            st.rerun()


# Página 3: Selección de colores
if st.session_state.page == 3:
    st.subheader("Selecciona los colores para tu outfit")

    colores_superior = sorted(productos_tageados[productos_tageados['Categoria'].str.contains('|'.join(st.session_state.tipos_superior), case=False)]['color_homogeneizado'].unique())
    colores_inferior = sorted(productos_tageados[productos_tageados['Categoria'].str.contains('Pantalón', case=False)]['color_homogeneizado'].unique())

    # Para la parte superior
    st.write("Colores para la parte superior:")

    # Botón "Seleccionar Todo" para los colores superiores
    if st.button("Seleccionar Todo" if not st.session_state.select_all_colores_superior else "Deseleccionar Todo", key="toggle_colores_superior"):
        st.session_state.select_all_colores_superior = not st.session_state.select_all_colores_superior
        if st.session_state.select_all_colores_superior:
            st.session_state.colores_superior = list(colores_superior)
        else:
            st.session_state.colores_superior = []
        st.rerun()

    # Crear un desplegable multiselección para los colores superiores
    seleccionados_superior = st.multiselect(
        "Selecciona los colores para la parte superior:",
        options=colores_superior,
        default=st.session_state.colores_superior
    )

    # Guardar la selección en session_state
    st.session_state.colores_superior = seleccionados_superior

    # Para la parte inferior
    st.write("Colores para la parte inferior:")

    # Botón "Seleccionar Todo" para los colores inferiores
    if st.button("Seleccionar Todo" if not st.session_state.select_all_colores_inferior else "Deseleccionar Todo", key="toggle_colores_inferior"):
        st.session_state.select_all_colores_inferior = not st.session_state.select_all_colores_inferior
        if st.session_state.select_all_colores_inferior:
            st.session_state.colores_inferior = list(colores_inferior)
        else:
            st.session_state.colores_inferior = []
        st.rerun()

    # Crear un desplegable multiselección para los colores inferiores
    seleccionados_inferior = st.multiselect(
        "Selecciona los colores para la parte inferior:",
        options=colores_inferior,
        default=st.session_state.colores_inferior
    )

    # Guardar la selección en session_state
    st.session_state.colores_inferior = seleccionados_inferior

    # Navegación entre páginas
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Siguiente", key="siguiente"):
            if st.session_state.colores_superior and st.session_state.colores_inferior:
                st.session_state.page = 4
                st.rerun()
            else:
                st.warning("Por favor, selecciona al menos un color para cada parte.")
    with col2:
        if st.button("Volver", key="volver"):
            st.session_state.page = 2
            st.rerun()


# Página 4: Selección de presupuesto
elif st.session_state.page == 4:
    st.subheader("Selecciona tu rango de presupuesto")

    # Obtener rangos dinámicos para las barras de presupuesto
    max_price_superior = productos_tageados[(productos_tageados['Categoria'].str.contains('|'.join(st.session_state.tipos_superior), case=False)) &
                              (productos_tageados['color_homogeneizado'].isin(st.session_state.colores_superior))]['current_price'].max() + 1
    min_price_superior = productos_tageados[(productos_tageados['Categoria'].str.contains('|'.join(st.session_state.tipos_superior), case=False)) &
                              (productos_tageados['color_homogeneizado'].isin(st.session_state.colores_superior))]['current_price'].min()

    max_price_inferior = productos_tageados[(productos_tageados['Categoria'].str.contains('Pantalón', case=False)) &
                              (productos_tageados['color_homogeneizado'].isin(st.session_state.colores_inferior))]['current_price'].max() + 1
    min_price_inferior = productos_tageados[(productos_tageados['Categoria'].str.contains('Pantalón', case=False)) &
                              (productos_tageados['color_homogeneizado'].isin(st.session_state.colores_inferior))]['current_price'].min()

    # Calcular el promedio dinámico para ambos rangos
    promedio_superior = (min_price_superior + max_price_superior) / 2
    promedio_inferior = (min_price_inferior + max_price_inferior) / 2

    # Verificar si los valores ya existen en session_state, si no, inicializarlos
    if 'presupuesto_superior' not in st.session_state:
        st.session_state.presupuesto_superior = (int(min_price_superior), int(promedio_superior))

    if 'presupuesto_inferior' not in st.session_state:
        st.session_state.presupuesto_inferior = (int(min_price_inferior), int(promedio_inferior))

    # Slider para rango de presupuesto superior
    st.session_state.presupuesto_superior = st.slider(
        "Rango de presupuesto para la parte superior (€):",
        min_value=int(min_price_superior),
        max_value=int(max_price_superior),
        value=st.session_state.presupuesto_superior  # Mantener el valor previo si existe
    )

    # Slider para rango de presupuesto inferior
    st.session_state.presupuesto_inferior = st.slider(
        "Rango de presupuesto para la parte inferior (€):",
        min_value=int(min_price_inferior),
        max_value=int(max_price_inferior),
        value=st.session_state.presupuesto_inferior  # Mantener el valor previo si existe
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Recomendar"):
            tags_aceptados_usuario_general = list(tag for sublist in st.session_state.aceptados_general for tag in sublist)
            tags_aceptados_usuario_superior= list(tag for sublist in st.session_state.aceptados_superior for tag in sublist)
            tags_aceptados_usuario_inferior= list(tag for sublist in st.session_state.aceptados_inferior for tag in sublist)
            tags_rechazados_usuario_general = list(tag for sublist in st.session_state.rechazados_general for tag in sublist)
            tags_rechazados_usuario_superior= list(tag for sublist in st.session_state.rechazados_superior for tag in sublist)
            tags_rechazados_usuario_inferior= list(tag for sublist in st.session_state.rechazados_inferior for tag in sublist)
            superiores = recomendador_superior(
                productos_tageados,
                tags_aceptados_usuario_general,
                tags_aceptados_usuario_superior,
                tags_rechazados_usuario_general,
                tags_rechazados_usuario_superior,
                st.session_state.tipos_superior,
                st.session_state.colores_superior,
                st.session_state.presupuesto_superior[0],  # Máximo del rango seleccionado para superior
                st.session_state.presupuesto_superior[1]   # Máximo del rango seleccionado para inferior
            )
            inferiores = recomendador_inferior(
                productos_tageados,
                tags_aceptados_usuario_general,
                tags_aceptados_usuario_inferior,
                tags_rechazados_usuario_general,
                tags_rechazados_usuario_inferior,
                st.session_state.colores_inferior,
                st.session_state.presupuesto_inferior[0],  # Máximo del rango seleccionado para superior
                st.session_state.presupuesto_inferior[1]   # Máximo del rango seleccionado para inferior
            )
            st.session_state.superiores = superiores.reset_index()
            st.session_state.inferiores = inferiores.reset_index()
            st.session_state.index_superior = 0  # Reiniciar índice superior
            st.session_state.index_inferior = 0  # Reiniciar índice inferior
            st.session_state.page = 5
            st.rerun()
    with col2:
        if st.button("Volver"):
            st.session_state.page = 3
            st.rerun()

# Página 5: Mostrar recomendaciones
if st.session_state.page == 5:
    st.subheader("Prendas recomendadas", divider="blue")

    presupuesto_superior = st.session_state.presupuesto_superior
    presupuesto_inferior = st.session_state.presupuesto_inferior

    if isinstance(presupuesto_superior, (int, float)):
        presupuesto_superior = [0, presupuesto_superior]
    if isinstance(presupuesto_inferior, (int, float)):
        presupuesto_inferior = [0, presupuesto_inferior]

    col_center = st.columns([1, 2, 1])[1]

    if 'superiores' in st.session_state and not st.session_state.superiores.empty:
        if 'index_superior' not in st.session_state:
            st.session_state.index_superior = 0
        
        sup_idx = st.session_state.index_superior
        if sup_idx >= len(st.session_state.superiores):
            sup_idx = len(st.session_state.superiores) - 1
        elif sup_idx < 0:
            sup_idx = 0
        
        superior = st.session_state.superiores.iloc[sup_idx]
        if superior['similaridad'] >= 0 and presupuesto_superior[0] <= superior['current_price'] <= presupuesto_superior[1]:
            with col_center:
                st.markdown(f"""
                <div class='image-container'>
                    <img src="{superior['image_url']}" style="max-width: 250px;">
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-size: 14px; font-weight: bold;'>{superior['product_name']} - {superior['current_price']}€</p>", unsafe_allow_html=True)
                # Botón similar a los de Streamlit
                if st.link_button("Ver producto", superior["url"]):
                    pass  # El botón de enlace no requiere acciones adicionales

                nav1, nav2 = st.columns([1, 1])
                with nav1:
                    if sup_idx < len(st.session_state.superiores) - 1:
                        if st.button("Siguiente prenda", key=f"siguiente_sup_{sup_idx}"):
                            st.session_state.index_superior += 1
                            st.rerun()
                with nav2:
                    if sup_idx > 0:
                        if st.button("Prenda anterior", key=f"anterior_sup_{sup_idx}"):
                            st.session_state.index_superior -= 1
                            st.rerun()

        else:
            st.warning("No hay opciones de parte superior dentro del presupuesto.")
    else:
        st.warning("No se encontraron prendas recomendadas para la parte superior.")

    if 'inferiores' in st.session_state and not st.session_state.inferiores.empty:
        if 'index_inferior' not in st.session_state:
            st.session_state.index_inferior = 0
        
        inf_idx = st.session_state.index_inferior
        if inf_idx >= len(st.session_state.inferiores):
            inf_idx = len(st.session_state.inferiores) - 1
        elif inf_idx < 0:
            inf_idx = 0
        
        inferior = st.session_state.inferiores.iloc[inf_idx]
        if inferior['similaridad'] >= 0 and presupuesto_inferior[0] <= inferior['current_price'] <= presupuesto_inferior[1]:
            with col_center:
                st.markdown(f"""
                <div class='image-container'>
                    <img src="{inferior['image_url']}" style="max-width: 250px;">
                </div>
                """, unsafe_allow_html=True)
                st.markdown(f"<p style='text-align: center; font-size: 14px; font-weight: bold;'>{inferior['product_name']} - {inferior['current_price']}€</p>", unsafe_allow_html=True)
                # Botón similar a los de Streamlit
                if st.link_button("Ver producto", inferior["url"]):
                    pass  # El botón de enlace no requiere acciones adicionales

                nav1, nav2 = st.columns([1, 1])
                with nav1:
                    if inf_idx < len(st.session_state.inferiores) - 1:
                        if st.button("Siguiente prenda", key=f"siguiente_inf_{inf_idx}"):
                            st.session_state.index_inferior += 1
                            st.rerun()
                with nav2:
                    if inf_idx > 0:
                        if st.button("Prenda anterior", key=f"anterior_inf_{inf_idx}"):
                            st.session_state.index_inferior -= 1
                            st.rerun()

        else:
            st.warning("No hay opciones de parte inferior dentro del presupuesto.")
    else:
        st.warning("No se encontraron prendas recomendadas para la parte inferior.")

    # Botones de navegación
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Volver a la página anterior"):
            st.session_state.page = 4
            st.rerun()
    with col2:
        if st.button("Reiniciar recomendador"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
