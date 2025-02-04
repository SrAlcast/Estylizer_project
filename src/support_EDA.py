# Tratamiento de datos
# -----------------------------------------------------------------------
import numpy as np
import pandas as pd

# Otros objetivos
# -----------------------------------------------------------------------
import math
import numpy as np
from itertools import product  # Para generar combinaciones
from tqdm import tqdm  # Para mostrar progreso


# Gráficos
# -----------------------------------------------------------------------
import seaborn as sns
import matplotlib.pyplot as plt

# Imputación de nulos usando métodos avanzados estadísticos
# -----------------------------------------------------------------------
from sklearn.impute import SimpleImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.impute import KNNImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.neighbors import LocalOutlierFactor 

def exploracion_basica_dataframe(dataframe):
    """
    Realiza un análisis exploratorio básico de un DataFrame, mostrando información sobre duplicados,
    valores nulos, tipos de datos, valores únicos para columnas categóricas y estadísticas descriptivas
    para columnas categóricas y numéricas, agrupadas por la columna de control.

    Params:
    - dataframe (DataFrame): El DataFrame que se va a explorar.
    - columna_control (str): El nombre de la columna que se utilizará como control para dividir el DataFrame.

    Returns: 
    No devuelve nada directamente, pero imprime en la consola la información exploratoria.
    """
    print(f"El número de datos es {dataframe.shape[0]} y el de columnas es {dataframe.shape[1]}")
    print("\n ------------------------------- \n")

    print(f"Los duplicados que tenemos en el conjunto de datos son: {dataframe.duplicated().sum()}")
    print("\n ------------------------------- \n")
    # generamos un DataFrame con cantidad de valores unicos
    print("Los unicos que tenemos en el conjunto de datos son:")
    df_unique = pd.DataFrame({
        "count": dataframe.nunique(),
        "% unique": (dataframe.nunique() / dataframe.shape[0] * 100).round(2)})
    # Ordenar por porcentaje de valores únicos en orden descendente
    df_unique_sorted = df_unique.sort_values(by="% unique", ascending=False)
    # Mostrar el resultado
    display(df_unique_sorted)
    columnas_mayor_50_unicos = df_unique_sorted[df_unique_sorted["% unique"] > 50].index.tolist()
    # Imprimimos los nombres de las columnas
    print("Las columnas con más del 50% de valores unicos son:")
    for col in columnas_mayor_50_unicos:
        print(col)
    print("\n ------------------------------- \n")
    columnas_solo_1_unico = df_unique_sorted[df_unique_sorted["count"] ==1].index.tolist()
    # Imprimimos los nombres de las columnas
    print("Las columnas con solo 1 valor único son:")
    for col in columnas_solo_1_unico:
        print(col)
    print("\n ------------------------------- \n")
    # generamos un DataFrame para los valores nulos
    df_nulos = pd.DataFrame({"count": dataframe.isnull().sum(),"% nulos": (dataframe.isnull().sum() / dataframe.shape[0]).round(3) * 100}).sort_values(by="% nulos", ascending=False)
    df_nulos = df_nulos[df_nulos["count"] > 0]
    df_nulos_sorted = df_nulos.sort_values(by="% nulos", ascending=False)
    # Muestra el resultado
    print("Los nulos que tenemos en el conjunto de datos son:")
    display(df_nulos_sorted)
    columnas_mayor_50 = df_nulos[df_nulos["% nulos"] > 50].index.tolist()

    # Imprimimos los nombres de las columnas
    print("Las columnas con más del 50% de valores nulos son:")
    for col in columnas_mayor_50:
        print(col)

    print("\n ------------------------------- \n")
    print(f"Los tipos de las columnas son:")
    display(pd.DataFrame(dataframe.dtypes, columns = ["tipo_dato"]))
    print("\n ------------------------------- \n")


    print("Los valores que tenemos para las columnas categóricas son: ")
    dataframe_categoricas = pd.DataFrame(dataframe.select_dtypes(include = "O"))
    display(pd.DataFrame(dataframe_categoricas.columns,columns=["columna"]))
    print("\n ------------------------------- \n")


    print("Los valores que tenemos para las columnas numéricas son: ")
    dataframe_numericas = pd.DataFrame(dataframe.select_dtypes(include = np.number))
    display(pd.DataFrame(dataframe_numericas.columns,columns=["columna"]))
    print("\n ------------------------------- \n")


    for col in dataframe_categoricas.columns:
        print(f"La columna {col.upper()} tiene las siguientes valore únicos:")
        if dataframe[col].isnull().sum()>0:
            print(f"--->La columna {col.upper()} tiene valores nulos")
        df_counts = pd.DataFrame({"count": dataframe[col].value_counts(dropna=False),"porcentaje (%)": (dataframe[col].value_counts(dropna=False, normalize=True) * 100).round(3)})
        display(df_counts)
        print("\n ------------------------------- \n")
    
    print("_______________________________________________________")
    print("Los valores que tenemos para las columnas numéricas son: ")
    dataframe_numericas = pd.DataFrame(dataframe.select_dtypes(include =np.number))
    
    for col in dataframe_numericas.columns:
        print(f"La columna {col.upper()} tiene las siguientes valore únicos:")
        if dataframe[col].isnull().sum()>0:
            print(f"--->La columna {col.upper()} tiene valores nulos")
        df_counts = pd.DataFrame({"count": dataframe[col].value_counts(dropna=False),"porcentaje (%)": (dataframe[col].value_counts(dropna=False, normalize=True) * 100).round(3)})
        display(df_counts)
        print("\n ------------------------------- \n")

def plot_numericas(dataframe):
    df_num=dataframe.select_dtypes(include=np.number)
    num_filas=math.ceil(len(df_num.columns)/2)
    fig, axes=plt.subplots(nrows=num_filas, ncols=2,figsize=(15,10))
    axes=axes.flat

    for indice, columna in enumerate(df_num.columns):
        sns.histplot(x=columna, data=df_num, ax=axes[indice])
        axes[indice].set_title(columna)
        axes[indice].set_xlabel("")

    if len(df_num.columns)%2!=0:
        fig.delaxes(axes[-1])  
    else:
        pass

    plt.tight_layout()


def plot_categoricas(dataframe, paleta="mako", max_categories=10):
    # Seleccionar solo columnas categóricas
    df_cat = dataframe.select_dtypes(include="O")
    
    # Filtrar columnas con menos de `max_categories` categorías únicas
    filtered_columns = [col for col in df_cat.columns if dataframe[col].nunique() <= max_categories]
    df_cat = df_cat[filtered_columns]
    
    num_columnas = 2  # Fijar el número de columnas por fila
    num_filas = math.ceil(len(df_cat.columns) / num_columnas)
    
    # Ajustar el tamaño de los gráficos
    fig, axes = plt.subplots(nrows=num_filas, ncols=num_columnas, figsize=(14, num_filas * 5))
    axes = axes.flat

    for indice, columna in enumerate(df_cat.columns):
        # Contar valores por categoría (incluidos nulos)
        category_counts = df_cat[columna].value_counts(dropna=False)
        
        # Separar los valores nulos como categoría aparte
        null_counts = df_cat[columna].isnull().sum()  # Total de nulos en la columna
        null_series = pd.Series(null_counts, index=["Nulos"]) if null_counts > 0 else pd.Series()

        # Combinar conteo de categorías con los valores nulos
        combined_counts = pd.concat([category_counts, null_series])
        
        # Crear el gráfico
        sns.barplot(
            x=combined_counts.index.astype(str),  # Aseguramos que sean strings
            y=combined_counts.values, 
            ax=axes[indice], 
            palette=paleta
        )
        
        # Configuración del gráfico
        axes[indice].set_title(columna, fontsize=14, weight="bold")  # Títulos más visibles
        axes[indice].set_xlabel("")  # Ocultar etiquetas del eje X
        axes[indice].tick_params(axis='x', rotation=45, labelsize=10)  # Rotar etiquetas
        axes[indice].set_ylabel("Count", fontsize=12)

    # Eliminar ejes vacíos si el número de gráficos no es par
    for i in range(len(df_cat.columns), len(axes)):
        fig.delaxes(axes[i])
    
    # Ajustar el espaciado entre subgráficos
    plt.tight_layout(pad=3.0)
    plt.suptitle("Análisis de Variables Categóricas (Incluyendo Nulos, ≤ {} Categorías)".format(max_categories), 
                 fontsize=18, weight="bold", y=1.02)
    
    plt.show()

def relacion_vr_categoricas(dataframe, variable_respuesta, paleta="mako", max_categories=10):
    # Seleccionar columnas categóricas con menos de `max_categories` categorías únicas
    df_cat = dataframe.select_dtypes(include="O").copy()
    filtered_columns = [col for col in df_cat.columns if dataframe[col].nunique() <= max_categories and col != variable_respuesta]
    
    if not filtered_columns:
        print(f"No hay columnas categóricas con menos de {max_categories} categorías para graficar.")
        return
    
    # Crear un gráfico para cada columna categórica
    for columna in filtered_columns:
        # Calcular el promedio de la variable respuesta por categoría
        datos_agrupados = dataframe.groupby(columna)[variable_respuesta].mean().reset_index()
        
        # Crear el gráfico
        plt.figure(figsize=(8, 5))
        sns.barplot(
            x=datos_agrupados[columna], 
            y=datos_agrupados[variable_respuesta], 
            palette=paleta
        )
        
        # Configuración del gráfico
        plt.title(f"Promedio de '{variable_respuesta}' por '{columna}'", fontsize=14, weight="bold")
        plt.xlabel(columna, fontsize=12)
        plt.ylabel(f"Promedio de {variable_respuesta}", fontsize=12)
        plt.xticks(rotation=45, ha="right", fontsize=10)
        plt.tight_layout()
        plt.show()

def relacion_vr_numericas_scatter(dataframe, variable_respuesta):
    # Seleccionar columnas numéricas excluyendo la variable respuesta
    df_num = dataframe.select_dtypes(include="number").drop(columns=[variable_respuesta], errors='ignore')
    
    if df_num.empty:
        print("No hay columnas numéricas para graficar.")
        return

    for columna in df_num.columns:
        plt.figure(figsize=(8, 5))
        sns.scatterplot(x=dataframe[columna], y=dataframe[variable_respuesta], alpha=0.7)
        
        plt.title(f"Relación entre '{columna}' y '{variable_respuesta}'", fontsize=14, weight="bold")
        plt.xlabel(columna, fontsize=12)
        plt.ylabel(variable_respuesta, fontsize=12)
        plt.tight_layout()
        plt.show()

def matriz_correlacion(dataframe):
    matriz_corr=dataframe.corr(numeric_only=True)
    mascara=np.triu(np.ones_like(matriz_corr,dtype=np.bool_))
    sns.heatmap(matriz_corr,
                annot=True,
                vmin=1,
                vmax=-1,
                mask=mascara,
                cmap="seismic")
    plt.figure(figsize=(10,15))
    plt.tight_layout()


def comparador_estaditicos(df_list, names=None):
    # Obtener las columnas en común entre todos los DataFrames
    common_columns = set(df_list[0].columns)
    for df in df_list[1:]:
        common_columns &= set(df.columns)
    common_columns = list(common_columns)

    # Lista para almacenar cada DataFrame descriptivo
    descriptive_dfs = []

    # Genera descripciones para cada DataFrame y las almacena
    for i, df in enumerate(df_list):
        desc_df = df[common_columns].describe().T  # Transpone y usa solo las columnas comunes
        desc_df['DataFrame'] = names[i] if names else f'DF_{i+1}'
        descriptive_dfs.append(desc_df)

    # Combina todos los DataFrames descriptivos en uno solo
    comparative_df = pd.concat(descriptive_dfs)
    comparative_df = comparative_df.set_index(['DataFrame', comparative_df.index])  # Índice jerárquico

    # Encuentra las diferencias por fila (compara cada estadística entre DataFrames)
    diff_df = comparative_df.groupby(level=1).apply(lambda x: x.nunique() > 1).any(axis=1)

    # Filtra solo las filas que tengan diferencias y verifica que los índices existen
    available_indices = comparative_df.index.get_level_values(1).unique()
    indices_with_diff = [index for index in diff_df[diff_df].index if index in available_indices]

    comparative_df_diff = comparative_df.loc[(slice(None), indices_with_diff), :]

    return comparative_df_diff


# Función para traducir columnas y contenido de todo el DataFrame
def translate_dataframe(df):
    """
    Traduce los nombres de columnas y el contenido de todo el DataFrame.
    """
    translation_dict_columns = {
    'propertyCode': 'Código Propiedad',
    'numPhotos': 'Número Fotos',
    'price': 'Precio',
    'propertyType': 'Tipo de Propiedad',
    'operation': 'Operación',
    'size': 'Tamaño',
    'exterior': 'Exterior',
    'rooms': 'Habitaciones',
    'bathrooms': 'Baños',
    'address': 'Dirección',
    'province': 'Provincia',
    'municipality': 'Municipio',
    'country': 'País',
    'latitude': 'Latitud',
    'longitude': 'Longitud',
    'showAddress': 'Mostrar Dirección',
    'distance': 'Distancia',
    'description': 'Descripción',
    'hasVideo': 'Tiene Video',
    'status': 'Estado',
    'newDevelopment': 'Nueva Construcción',
    'priceByArea': 'Precio Por Área',
    'detailedType': 'Tipo Detallado',
    'suggestedTexts': 'Textos Sugeridos',
    'hasPlan': 'Tiene Plano',
    'has3DTour': 'Tiene Tour 3D',
    'has360': 'Tiene 360',
    'hasStaging': 'Tiene Diseño Virtual',
    'superTopHighlight': 'Súper Destacado',
    'topNewDevelopment': 'Desarrollo Destacado',
    'externalReference': 'Referencia Externa',
    'floor': 'Piso',
    'district': 'Distrito',
    'neighborhood': 'Vecindario',
    'hasLift': 'Ascensor',
    'parkingSpace': 'Garaje',
    'labels': 'Etiquetas',
    'newDevelopmentFinished': 'Nueva Construcción Terminada'}

    # Traducir nombres de columnas
    df = df.rename(columns=translation_dict_columns)
    return df

# GESTION OUTIERS

def separar_dataframe(dataframe):
    return dataframe.select_dtypes(include = np.number), dataframe.select_dtypes(include = "O")

def detectar_outliers(dataframe, color="blue", tamano_grafica=(15,10)):
    df_num = separar_dataframe(dataframe)[0]

    num_filas = math.ceil(len(df_num.columns) / 2)

    fig, axes = plt.subplots(ncols=2, nrows=num_filas, figsize=tamano_grafica)
    axes = axes.flat

    for indice, columna in enumerate(df_num.columns):
        sns.boxplot(
            x=columna,
            data=df_num,
            ax=axes[indice],
            color=color,
            flierprops={"marker": "o", "markerfacecolor": "red", "markersize": 5}
        )
        
        axes[indice].set_title(f"Outliers de {columna}")
        axes[indice].set_xlabel("")

    if len(df_num.columns) % 2 != 0:
        fig.delaxes(axes[-1])
    else:
        pass

    plt.tight_layout()
    plt.show()


def scatterplot_outliers(dataframe, combinaciones_variables, columnas_hue, palette="Set1", alpha=0.5):
    """
    Visualización mejorada de gráficos de dispersión para analizar outliers.
    """
    for col_hue in columnas_hue:
        num_combinaciones = len(combinaciones_variables)
        num_filas = math.ceil(num_combinaciones / 3)  # Ajustar automáticamente el número de filas
        fig, axes = plt.subplots(ncols=3, nrows=num_filas, figsize=(15, 5 * num_filas))
        axes = axes.flat

        for indice, tupla in enumerate(combinaciones_variables):
            sns.scatterplot(
                data=dataframe,
                x=tupla[0],
                y=tupla[1],
                ax=axes[indice],
                hue=col_hue,
                palette=palette,
                style=col_hue,
                alpha=alpha
            )
            axes[indice].set_title(f"{tupla[0]} vs {tupla[1]} (hue: {col_hue})", fontsize=10)
            axes[indice].tick_params(axis='x', rotation=45)

        # Ocultar ejes vacíos si sobran
        for i in range(len(combinaciones_variables), len(axes)):
            axes[i].set_visible(False)

        plt.suptitle(f"Scatterplots con hue: {col_hue}", fontsize=16)
        plt.tight_layout()
        plt.show()

def gestion_nulos_lof(df, col_numericas, list_neighbors, lista_contaminacion):
    """
    Aplica el algoritmo LOF (Local Outlier Factor) para detectar outliers en las columnas numéricas del DataFrame.
    
    Args:
        df (pd.DataFrame): DataFrame que contiene los datos.
        col_numericas (list): Lista de nombres de columnas numéricas sobre las que aplicar LOF.
        list_neighbors (list): Lista de valores para el número de vecinos (`n_neighbors`).
        lista_contaminacion (list): Lista de valores para la tasa de contaminación (`contamination`).
    
    Returns:
        pd.DataFrame: DataFrame con nuevas columnas que indican outliers (-1) o inliers (1) para cada combinación de parámetros.
    """
    # Validar si las columnas numéricas existen en el DataFrame
    missing_columns = [col for col in col_numericas if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Las columnas {missing_columns} no están presentes en el DataFrame.")

    # Generar combinaciones de parámetros
    combinaciones = list(product(list_neighbors, lista_contaminacion))
    
    # Progresión y cálculo de LOF para cada combinación
    for neighbors, contaminacion in tqdm(combinaciones, desc="Aplicando LOF con diferentes parámetros"):
        # Inicializar el modelo LOF
        lof = LocalOutlierFactor(
            n_neighbors=neighbors, 
            contamination=contaminacion,
            n_jobs=-1
        )
        
        # Crear una nueva columna para la combinación de parámetros
        columna_nombre = f"outliers_lof_{neighbors}_{contaminacion}"
        df[columna_nombre] = lof.fit_predict(df[col_numericas])
    
    return df

def detectar_metricas(dataframe, color="orange", tamaño_grafica=(15,10)):
    df_num = dataframe.select_dtypes(include=np.number)
    num_filas = math.ceil(len(df_num.columns) / 2)
    fig, axes = plt.subplots(nrows=num_filas, ncols=2, figsize=tamaño_grafica)
    axes = axes.flat

    # Configuración de los outliers en color naranja
    flierprops = dict(marker='o', markerfacecolor='orange', markersize=5, linestyle='none')

    for indice, columna in enumerate(df_num.columns):
        sns.boxplot(x=columna,
                    data=df_num,
                    ax=axes[indice],
                    color=color,
                    flierprops=flierprops)  # Aplica color naranja a los outliers
        axes[indice].set_title(f"Outliers de {columna}")
        axes[indice].set_xlabel("")

    # Eliminar el último subplot si el número de columnas es impar
    if len(df_num.columns) % 2 != 0:
        fig.delaxes(axes[-1])
    
    plt.tight_layout()

def detectar_outliers_categoricos(dataframe, threshold=0.05):
    """
    Detecta valores categóricos raros (outliers) en variables categóricas basándose en su frecuencia en el DataFrame.
    
    Args:
        dataframe (pd.DataFrame): El DataFrame que contiene los datos.
        threshold (float): Umbral mínimo de frecuencia relativa para considerar un valor como no raro.
                           Valores por debajo de este umbral se consideran raros.
    
    Returns:
        dict: Un diccionario donde las claves son las columnas categóricas y los valores son listas de categorías raras.
    """
    # Seleccionar solo columnas categóricas
    columnas_categoricas = dataframe.select_dtypes(include='object').columns
    
    # Diccionario para almacenar los valores categóricos raros
    outliers_categoricos = {}
    
    for columna in columnas_categoricas:
        # Calcular la frecuencia relativa de cada categoría
        frecuencias = dataframe[columna].value_counts(normalize=True)
        
        # Filtrar las categorías con frecuencia menor al umbral
        valores_raros = frecuencias[frecuencias < threshold].index.tolist()
        
        # Almacenar los valores raros si existen
        if valores_raros:
            outliers_categoricos[columna] = valores_raros
    
    return outliers_categoricos

    # Filtrar el DataFrame
def filtrar_por_alguna_condicion(dataframe, condiciones):
    filtro = pd.Series(False, index=dataframe.index)  # Empezar con un filtro "falso"
    
    for columna, valores in condiciones.items():
        if columna in dataframe.columns:
            # Aplicar la condición para cada columna
            filtro |= dataframe[columna].isin(valores)
        else:
            print(f"Advertencia: La columna '{columna}' no está en el DataFrame.")
    
    # Aplicar el filtro al DataFrame
    return dataframe[filtro]

def generador_boxplots(df_list):
    # Filtra los DataFrames válidos
    df_list = [df for df in df_list if isinstance(df, pd.DataFrame)]
    
    if not df_list:
        print("Error: La lista no contiene DataFrames válidos.")
        return

    # Define los sufijos deseados
    sufijos_deseados = ('_stds', '_norm', '_minmax', '_robust')

    # Filtra las columnas de cada DataFrame para incluir solo las que tienen los sufijos deseados
    filtered_df_list = [df[[col for col in df.columns if col.endswith(sufijos_deseados)]] for df in df_list]

    # Configura la figura con una fila de subplots por DataFrame
    fig, axes = plt.subplots(nrows=len(filtered_df_list), ncols=max(len(df.columns) for df in filtered_df_list),
                             figsize=(6 * max(len(df.columns) for df in filtered_df_list), 4 * len(filtered_df_list)),
                             squeeze=False)  # Squeeze=False asegura una matriz 2D

    # Itera sobre cada DataFrame filtrado y cada columna
    for df_idx, df in enumerate(filtered_df_list):
        for col_idx, column in enumerate(df.columns):
            sns.boxplot(x=column, data=df, ax=axes[df_idx][col_idx])
            axes[df_idx][col_idx].set_title(f"DF {df_idx + 1} - {column}")

    # Oculta los ejes vacíos si hay menos columnas en algún DataFrame
    for df_idx, ax_row in enumerate(axes):
        for col_idx in range(len(filtered_df_list[df_idx].columns), axes.shape[1]):
            ax_row[col_idx].axis('off')

    # Ajuste de espaciado entre subplots
    plt.tight_layout()
    plt.show()

# ENCODING

def crear_boxplot(dataframe, lista_variables, variable_respuesta, whis=1.5, color="blue", tamano_grafica_base=(20, 5)):
    """
    Crea un boxplot para cada variable categórica en el conjunto de datos con una visualización mejorada.

    Parámetros:
    - dataframe: DataFrame que contiene los datos.
    - lista_variables: Lista de variables categóricas para generar los boxplots.
    - variable_respuesta: Variable respuesta para graficar en el eje y.
    - whis: El ancho de los bigotes. Por defecto es 1.5.
    - color: Color de los boxplots. Por defecto es "blue".
    - tamano_grafica_base: Tamaño base de cada fila de gráficos. Por defecto es (20, 5).
    """
    num_variables = len(lista_variables)
    num_filas = math.ceil(num_variables / 2)
    
    # Ajustar el tamaño de la figura dinámicamente
    tamano_grafica = (tamano_grafica_base[0], tamano_grafica_base[1] * num_filas)
    
    fig, axes = plt.subplots(num_filas, 2, figsize=tamano_grafica)
    axes = axes.flat

    for indice, columna in enumerate(lista_variables):
        sns.boxplot(
            y=variable_respuesta,
            x=columna,
            data=dataframe,
            color=color,
            ax=axes[indice],
            whis=whis,
            flierprops={'markersize': 4, 'markerfacecolor': 'orange'}
        )
        axes[indice].set_title(f'Boxplot: {columna}', fontsize=12)  # Título de cada subgráfico
        axes[indice].tick_params(axis='x', rotation=45)  # Rotar etiquetas del eje X

    # Ocultar los ejes restantes si hay un número impar de gráficos
    for ax in axes[num_variables:]:
        ax.axis('off')

    # Ajustar diseño general
    fig.tight_layout()
    plt.show()


def crear_barplot(dataframe, lista_variables, variable_respuesta, paleta="viridis", tamano_grafica_base=(20, 10)):
    """
    Crea un barplot para cada variable categórica en el conjunto de datos con una visualización mejorada.

    Parámetros:
    - dataframe: DataFrame que contiene los datos.
    - lista_variables: Lista de variables categóricas para generar los barplots.
    - variable_respuesta: Variable respuesta para calcular la media en cada categoría.
    - paleta: Paleta de colores para el barplot. Por defecto es "viridis".
    - tamano_grafica_base: Tamaño base de cada fila de gráficos. Por defecto es (20, 5).
    """
    num_variables = len(lista_variables)
    num_filas = math.ceil(num_variables / 2)
    
    # Ajustar tamaño de la figura dinámicamente
    tamano_grafica = (tamano_grafica_base[0], tamano_grafica_base[1] * num_filas)
    
    fig, axes = plt.subplots(num_filas, 2, figsize=tamano_grafica)
    axes = axes.flat

    for indice, columna in enumerate(lista_variables):
        # Calcular la media agrupada por categorías
        categoria_mediana = (
            dataframe.groupby(columna)[variable_respuesta]
            .mean()
            .reset_index()
            .sort_values(by=variable_respuesta)
        )

        # Crear el barplot
        sns.barplot(
            x=categoria_mediana[columna],
            y=categoria_mediana[variable_respuesta],
            palette=paleta,
            ax=axes[indice],
            errorbar='ci'
        )

        # Agregar títulos y ajustar etiquetas
        axes[indice].set_title(f"Media de {variable_respuesta} por {columna}", fontsize=12)
        axes[indice].tick_params(axis='x', rotation=45)

    # Ocultar los ejes sobrantes si el número de gráficos es impar
    for ax in axes[num_variables:]:
        ax.axis('off')

    # Ajustar diseño general
    fig.tight_layout()
    plt.show()

from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, LabelEncoder
from category_encoders import TargetEncoder

def one_hot_encoding(dataframe, columns):
    """
    Realiza codificación one-hot en las columnas especificadas.

    Args:
        dataframe (pd.DataFrame): DataFrame de pandas.
        columns (list): Lista de columnas a codificar.

    Returns:
        pd.DataFrame: DataFrame con codificación one-hot aplicada.
    """
    one_hot_encoder = OneHotEncoder()
    trans_one_hot = one_hot_encoder.fit_transform(dataframe[columns])
    oh_df = pd.DataFrame(trans_one_hot.toarray(), columns=one_hot_encoder.get_feature_names_out(columns))
    dataframe = pd.concat([dataframe.reset_index(drop=True), oh_df.reset_index(drop=True)], axis=1)
    dataframe.drop(columns=columns, inplace=True)
    return dataframe


def get_dummies_encoding(dataframe, columns, prefix=None, prefix_sep="_"):
    """
    Realiza codificación get_dummies en las columnas especificadas.

    Args:
        dataframe (pd.DataFrame): DataFrame de pandas.
        columns (list): Lista de columnas a codificar.
        prefix (str o dict, opcional): Prefijo para las columnas codificadas.
        prefix_sep (str): Separador entre el prefijo y la columna original.

    Returns:
        pd.DataFrame: DataFrame con codificación get_dummies aplicada.
    """
    df_dummies = pd.get_dummies(dataframe[columns], dtype=int, prefix=prefix, prefix_sep=prefix_sep)
    dataframe = pd.concat([dataframe.reset_index(drop=True), df_dummies.reset_index(drop=True)], axis=1)
    dataframe.drop(columns=columns, inplace=True)
    return dataframe


def ordinal_encoding(dataframe, columns, categories):
    """
    Realiza codificación ordinal en las columnas especificadas.

    Args:
        dataframe (pd.DataFrame): DataFrame de pandas.
        columns (list): Lista de columnas a codificar.
        categories (list of list): Lista de listas con las categorías en orden.

    Returns:
        pd.DataFrame: DataFrame con codificación ordinal aplicada.
    """
    ordinal_encoder = OrdinalEncoder(categories=categories, dtype=float, handle_unknown="use_encoded_value", unknown_value=np.nan)
    dataframe[columns] = ordinal_encoder.fit_transform(dataframe[columns])
    return dataframe


def label_encoding(dataframe, columns):
    """
    Realiza codificación label en las columnas especificadas.

    Args:
        dataframe (pd.DataFrame): DataFrame de pandas.
        columns (list): Lista de columnas a codificar.

    Returns:
        pd.DataFrame: DataFrame con codificación label aplicada.
    """
    label_encoder = LabelEncoder()
    for col in columns:
        dataframe[col] = label_encoder.fit_transform(dataframe[col])
    return dataframe


def target_encoding(dataframe, columns, target):
    """
    Realiza codificación target en las columnas especificadas.

    Args:
        dataframe (pd.DataFrame): DataFrame de pandas.
        columns (list): Lista de columnas a codificar.
        target (str): Nombre de la variable objetivo.

    Returns:
        pd.DataFrame: DataFrame con codificación target aplicada.
    """
    target_encoder = TargetEncoder(cols=columns)
    dataframe[columns] = target_encoder.fit_transform(dataframe[columns], dataframe[target])
    return dataframe


def frequency_encoding(dataframe, columns):
    """
    Realiza codificación de frecuencia en las columnas especificadas.

    Args:
        dataframe (pd.DataFrame): DataFrame de pandas.
        columns (list): Lista de columnas a codificar.

    Returns:
        pd.DataFrame: DataFrame con codificación de frecuencia aplicada.
    """
    for col in columns:
        freq_map = dataframe[col].value_counts(normalize=True)
        dataframe[col] = dataframe[col].map(freq_map)
    return dataframe
