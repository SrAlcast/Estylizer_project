import streamlit as st
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import random

# Función principal del recomendador
def recomendador_ropa_ml(data, tags_usuario, tipos_superior, colores_superior, colores_inferior, presupuesto_superior, presupuesto_inferior):
    vectorizer = CountVectorizer()
    data['tags_combined'] = data['description'].fillna('')
    tags_matrix = vectorizer.fit_transform(data['tags_combined'])
    tags_usuario_str = ' '.join(tags_usuario)
    user_vector = vectorizer.transform([tags_usuario_str])
    similitudes = cosine_similarity(user_vector, tags_matrix).flatten()
    data['similaridad'] = similitudes

    superiores = data[(data['Categoria'].str.contains('|'.join(tipos_superior), case=False)) &
                      (data['color_homogeneizado'].isin(colores_superior)) &
                      (data['current_price'] <= presupuesto_superior)]
    inferiores = data[(data['Categoria'].str.contains('Pantalón', case=False)) &
                      (data['color_homogeneizado'].isin(colores_inferior)) &
                      (data['current_price'] <= presupuesto_inferior)]

    superiores = superiores.sort_values(by=['similaridad', 'current_price'], ascending=[False, True])
    inferiores = inferiores.sort_values(by=['similaridad', 'current_price'], ascending=[False, True])

    return superiores, inferiores

# Cargar datos de estilos con imágenes
estilos_data = pd.read_csv("../results/pants_jeans_with_style_tags.csv")
data = pd.read_csv("../results/all_products_with_tags_added.csv")
data['current_price'] = pd.to_numeric(data['current_price'], errors='coerce')

# Interfaz de Streamlit
st.title("Recomendador de Outfits")

# Variables para el estado
if 'aceptados' not in st.session_state:
    st.session_state.aceptados = []
if 'rechazados' not in st.session_state:
    st.session_state.rechazados = []
if 'estilo_index' not in st.session_state:
    st.session_state.estilo_index = 0
if 'finalizado_estilos' not in st.session_state:
    st.session_state.finalizado_estilos = False
if 'random_indices' not in st.session_state:
    st.session_state.random_indices = random.sample(range(len(estilos_data)), 8)
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'tipos_superior' not in st.session_state:
    st.session_state.tipos_superior = []
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

# Centrar contenido y personalizar estilos
def centrar_contenido():
    st.markdown(
        """
        <style>
        .block-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }
        .button-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            width: 100%;
            max-width: 600px;
            margin-top: 20px;
        }
        .stButton > button {
            margin: 0 20px;
        }
        img {
            display: block;
            margin: 20px auto;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

centrar_contenido()

# Página 1: Selección de estilos
if st.session_state.page == 1:
    if st.session_state.estilo_index < 8:
        estilo = estilos_data.iloc[st.session_state.random_indices[st.session_state.estilo_index]]

        # Mostrar imagen y botones
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if st.button("No me gusta", key=f"dislike_{st.session_state.estilo_index}"):
                st.session_state.rechazados.append(estilo['style_tags'])
                st.session_state.estilo_index += 1
                st.experimental_rerun()
        with col2:
            st.image(estilo['Image 1 URL'], width=250)
        with col3:
            if st.button("Me gusta", key=f"like_{st.session_state.estilo_index}"):
                st.session_state.aceptados.append(estilo['style_tags'])
                st.session_state.estilo_index += 1
                st.experimental_rerun()
        # Mostrar barra de progreso
        progreso = (st.session_state.estilo_index + 1) / 8
        st.progress(progreso)

        # Botón para resetear todo
        st.markdown("<hr>", unsafe_allow_html=True)
        if st.button("Resetear todo"):
            resetear_estado()
            st.experimental_rerun()

    else:
        st.success("Has terminado de seleccionar estilos.")
        st.session_state.page = 2
        st.experimental_rerun()

# Página 2: Selección de tipo de parte superior
if st.session_state.page == 2:
    st.subheader("¿Qué tipo de prenda quieres para la parte superior? (Selecciona múltiples opciones)")

    tipos = ["Camiseta", "Camisa", "Sudadera"]
    for tipo in tipos:
        if tipo in st.session_state.tipos_superior:
            if st.button(f"✅ {tipo}", key=f"tipo_{tipo}"):
                st.session_state.tipos_superior.remove(tipo)
                st.experimental_rerun()
        else:
            if st.button(tipo, key=f"tipo_{tipo}"):
                st.session_state.tipos_superior.append(tipo)
                st.experimental_rerun()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Volver"):
            st.session_state.page = 1
            st.experimental_rerun()
    with col2:
        if st.button("Siguiente"):
            if st.session_state.tipos_superior:
                st.session_state.page = 3
                st.experimental_rerun()
            else:
                st.warning("Por favor, selecciona al menos un tipo de prenda.")

# Página 3: Selección de colores
elif st.session_state.page == 3:
    st.subheader("Selecciona los colores para tu outfit (Selecciona múltiples opciones)")

    colores_superior = data[data['Categoria'].str.contains('|'.join(st.session_state.tipos_superior), case=False)]['color_homogeneizado'].unique()
    colores_inferior = data[data['Categoria'].str.contains('Pantalón', case=False)]['color_homogeneizado'].unique()

    st.write("Colores para la parte superior:")
    for color in colores_superior:
        if color in st.session_state.colores_superior:
            if st.button(f"✅ {color}", key=f"color_sup_{color}"):
                st.session_state.colores_superior.remove(color)
                st.experimental_rerun()
        else:
            if st.button(color, key=f"color_sup_{color}"):
                st.session_state.colores_superior.append(color)
                st.experimental_rerun()

    st.write("Colores para la parte inferior:")
    for color in colores_inferior:
        if color in st.session_state.colores_inferior:
            if st.button(f"✅ {color}", key=f"color_inf_{color}"):
                st.session_state.colores_inferior.remove(color)
                st.experimental_rerun()
        else:
            if st.button(color, key=f"color_inf_{color}"):
                st.session_state.colores_inferior.append(color)
                st.experimental_rerun()

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Volver"):
            st.session_state.page = 2
            st.experimental_rerun()
    with col2:
        if st.button("Siguiente"):
            if st.session_state.colores_superior and st.session_state.colores_inferior:
                st.session_state.page = 4
                st.experimental_rerun()
            else:
                st.warning("Por favor, selecciona al menos un color para cada parte.")

# Página 4: Selección de presupuesto
elif st.session_state.page == 4:
    st.subheader("Selecciona tu presupuesto máximo")

    # Obtener rangos dinámicos para las barras de presupuesto
    max_price_superior = data[(data['Categoria'].str.contains('|'.join(st.session_state.tipos_superior), case=False)) &
                              (data['color_homogeneizado'].isin(st.session_state.colores_superior))]['current_price'].max() + 1
    min_price_superior = data[(data['Categoria'].str.contains('|'.join(st.session_state.tipos_superior), case=False)) &
                              (data['color_homogeneizado'].isin(st.session_state.colores_superior))]['current_price'].min() + 1

    max_price_inferior = data[(data['Categoria'].str.contains('Pantalón', case=False)) &
                              (data['color_homogeneizado'].isin(st.session_state.colores_inferior))]['current_price'].max() + 1
    min_price_inferior = data[(data['Categoria'].str.contains('Pantalón', case=False)) &
                              (data['color_homogeneizado'].isin(st.session_state.colores_inferior))]['current_price'].min() + 1

    st.session_state.presupuesto_superior = st.slider(
        "Presupuesto máximo para la parte superior (€):",
        min_value=int(min_price_superior), max_value=int(max_price_superior), value=int((min_price_superior + max_price_superior) / 2)
    )

    st.session_state.presupuesto_inferior = st.slider(
        "Presupuesto máximo para la parte inferior (€):",
        min_value=int(min_price_inferior), max_value=int(max_price_inferior), value=int((min_price_inferior + max_price_inferior) / 2)
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Volver"):
            st.session_state.page = 3
            st.experimental_rerun()
    with col2:
        if st.button("Recomendar"):
            tags_usuario = list(set([tag for sublist in st.session_state.aceptados for tag in sublist.split(', ')]))
            superiores, inferiores = recomendador_ropa_ml(
                data,
                tags_usuario,
                st.session_state.tipos_superior,
                st.session_state.colores_superior,
                st.session_state.colores_inferior,
                st.session_state.presupuesto_superior,
                st.session_state.presupuesto_inferior
            )
            st.session_state.superiores = superiores.reset_index()
            st.session_state.inferiores = inferiores.reset_index()
            st.session_state.index_superior = 0  # Reiniciar índice superior
            st.session_state.index_inferior = 0  # Reiniciar índice inferior
            st.session_state.page = 5
            st.experimental_rerun()


# Página 5: Mostrar recomendaciones
elif st.session_state.page == 5:
    st.subheader("Prendas recomendadas")

    # Mostrar parte superior
    if 'superiores' in st.session_state and not st.session_state.superiores.empty:
        sup_idx = st.session_state.index_superior
        if sup_idx < len(st.session_state.superiores):
            superior = st.session_state.superiores.iloc[sup_idx]

        if superior['current_price'] <= st.session_state.presupuesto_superior:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(superior['image_url'] if isinstance(superior['image_url'], str) else 'https://via.placeholder.com/150', width=150)
            with col2:
                st.write("Parte Superior")
                st.write(f"**Nombre:** {superior['Product Name']}")
                st.write(f"**Precio:** {superior['current_price']}€")
                st.write(f"**Color:** {superior['color_homogeneizado']}")
                st.write(f"[Ver producto]({superior['url']})")
                navigation_col1, navigation_col2 = st.columns([1, 1])
                with navigation_col1:
                    if st.session_state.index_superior > 0:
                        if st.button("Anterior", key=f"anterior_sup_{st.session_state.index_superior}"):
                            st.session_state.index_superior -= 1
                            st.experimental_rerun()
                with navigation_col2:
                    if st.session_state.index_superior < len(st.session_state.superiores) - 1:
                        if st.button("Siguiente", key=f"siguiente_sup_{st.session_state.index_superior}"):
                            st.session_state.index_superior += 1
                            st.experimental_rerun()
        else:
            st.warning("No hay opciones de parte superior dentro del presupuesto.")

    # Mostrar parte inferior
    if 'inferiores' in st.session_state and not st.session_state.inferiores.empty:
        inf_idx = st.session_state.index_inferior
        if inf_idx < len(st.session_state.inferiores):
            inferior = st.session_state.inferiores.iloc[inf_idx]

        if inferior['current_price'] <= st.session_state.presupuesto_inferior:
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(inferior['image_url'] if isinstance(inferior['image_url'], str) else 'https://via.placeholder.com/150', width=150)
            with col2:
                st.write("Parte Inferior")
                st.write(f"**Nombre:** {inferior['Product Name']}")
                st.write(f"**Precio:** {inferior['current_price']}€")
                st.write(f"**Color:** {inferior['color_homogeneizado']}")
                st.write(f"[Ver producto]({inferior['url']})")
                navigation_col1, navigation_col2 = st.columns([1, 1])
                with navigation_col1:
                    if st.session_state.index_inferior > 0:
                        if st.button("Anterior", key=f"anterior_inf_{st.session_state.index_inferior}"):
                            st.session_state.index_inferior -= 1
                            st.experimental_rerun()
                with navigation_col2:
                    if st.session_state.index_inferior < len(st.session_state.inferiores) - 1:
                        if st.button("Siguiente", key=f"siguiente_inf_{st.session_state.index_inferior}"):
                            st.session_state.index_inferior += 1
                            st.experimental_rerun()
        else:
            st.warning("No hay opciones de parte inferior dentro del presupuesto.")

    # Botones de navegación adicional
    st.markdown("---")
    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Volver a la página anterior"):
            st.session_state.page = 4
            st.experimental_rerun()
    with col2:
        if st.button("Reiniciar recomendador"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.experimental_rerun()
