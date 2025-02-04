import pandas as pd
import requests
import base64
import time
from io import BytesIO
from anthropic import Anthropic
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv(dotenv_path="..\src\.env")

# Leer las variables de entorno
api__key = os.getenv("api_key")

def tag_models(df, api_key=api__key):
    """
    Toma un DataFrame con una columna 'url' y devuelve un DataFrame con seis columnas adicionales de tags.

    Parameters:
    df (pd.DataFrame): DataFrame con una columna 'url' que contiene las URLs de las imágenes.
    api_key (str): Clave de API de Anthropic.

    Returns:
    pd.DataFrame: DataFrame con las seis columnas de tags agregadas.
    """
    # Inicializar el cliente de Anthropic con el argumento nombrado api_key
    client = Anthropic(api_key=api_key)

    # Copia del DataFrame
    df_result = df.copy()

    # Agregar columnas para los tags
    tag_columns = [f'Tag_{i+1}' for i in range(6)]
    for col in tag_columns:
        df_result[col] = None

    for index, row in df.iterrows():
        image_url = row['image1_url']
        product_description = row.get('description')  # Si existe la columna 'description', úsala
        
        try:
            # Descargar la imagen
            response = requests.get(image_url)
            image_data = BytesIO(response.content)

            # Convertir la imagen a base64
            base64_image = base64.b64encode(image_data.read()).decode('utf-8')

            # Crear el mensaje para Claude con instrucciones
            message_content = f"""
            Por favor, analiza la imagen proporcionada y clasifica el conjunto y la ropa observada en las siguientes categorías, asegurando que la selección sea coherente con la descripción del pantalón. Usa exclusivamente DOS palabras de cada lista.
            Descripción del pantalón: "{product_description}"
            ESTILO GENERAL (elige dos, según el conjunto completo): Casual, Formal, Vintage, Elegante, Deportivo, Streetwear, Clásico, Minimalista, Bohemio, Moderno, Monocromático.
            PARTE SUPERIOR (elige dos, considerando ajuste y diseño de la parte superior del conjunto): Ajustada, Oversize, Cuello alto, Manga corta, Manga larga, Sin mangas, Color claro, Color oscuro, Estampado, Deportivo.
            PARTE INFERIOR (elige dos, en función del pantalón descrito y observado en la imagen): Joggers, Baggy, Cargo, Tailoring, Skater, Standard, Slim, Straight, Rasgado, Carrot, Skinny, Ajustado, Deportivo, Chándal.
            Asegúrate de que la clasificación refleje fielmente la apariencia visual y la descripción del pantalón, manteniendo coherencia en la elección de términos.
            EL FORMATO DE LA RESPUESTA DEBE SER UNICAMENTE:"Estilo1, Estilo2, Superior1, Superior2, Inferior1, Inferior2"
            """

            # Enviar el mensaje a Claude
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message_content},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}}
                    ]
                }]
            )

            # Extraer los tags de la respuesta
            if isinstance(message.content, list):
                tags_text = message.content[0].text
            else:
                tags_text = message.content

            # Procesar los tags en columnas
            tags = tags_text.replace('\n', ', ').split(', ')
            if len(tags) == 6:
                df_result.loc[index, tag_columns] = tags

        except Exception as e:
            print(f"Error procesando la imagen {image_url}: {e}")

        time.sleep(1)  # Evitar restricciones de la API
        
    return df_result

def tag_products_superior(df, api_key=api__key):
    """
    Toma un DataFrame con una columna 'url' y devuelve un DataFrame con tres columnas adicionales de tags.

    Parameters:
    df (pd.DataFrame): DataFrame con una columna 'url' que contiene las URLs de los productos.
    api_key (str): Clave de API de Anthropic.

    Returns:
    pd.DataFrame: DataFrame con tres columnas de tags agregadas.
    """
    client = Anthropic(api_key=api_key)
    df_result = df.copy()
    
    # Agregar columnas para los tags
    tag_columns = [f'Tag_{i+1}' for i in range(3)]
    for col in tag_columns:
        df_result[col] = None
    
    for index, row in df.iterrows():
        image_url = row['image_url']
        product_description = row.get('description')  # Usar descripción si está disponible
        print(product_description)
        try:
            response = requests.get(image_url)
            image_data = BytesIO(response.content)
            base64_image = base64.b64encode(image_data.read()).decode('utf-8')

            message_content = f"""
            Analiza la imagen del producto y clasifícalo en tres categorías principales. Usa exclusivamente UNA palabra de cada lista.
            Descripción del producto: "{product_description}"
            
            ESTILO (elige una): Casual, Formal, Vintage, Elegante, Deportivo, Streetwear, Clásico, Minimalista, Bohemio, Moderno, Monocromático.
            CATEGORÍA PRINCIPAL (elige una): Ajustada, Oversize, Cuello alto, Manga corta, Manga larga, Sin mangas, Color claro, Color oscuro, Estampado, Deportivo.
            CATEGORÍA SECUNDARIA (elige una): Ajustada, Oversize, Cuello alto, Manga corta, Manga larga, Sin mangas, Color claro, Color oscuro, Estampado, Deportivo.

            Asegúrate de que la clasificación refleje fielmente la apariencia y descripción del producto, la cateogoria principal y la secundaria deben ser diferentes.
            EL FORMATO DE RESPUESTA DEBE SER ÚNICAMENTE: "ESTILO, CATEGORÍA PRINCIPAL, CATEGORÍA SECUNDARIA"
            """
            
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message_content},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}}
                    ]
                }]
            )
            
            tags_text = message.content[0].text if isinstance(message.content, list) else message.content
            tags = tags_text.replace('\n', ', ').split(', ')
            if len(tags) == 3:
                df_result.loc[index, tag_columns] = tags

        except Exception as e:
            print(f"Error procesando la imagen {image_url}: {e}")
        
        time.sleep(1)  # Evitar restricciones de la API
        
    return df_result

def tag_products_inferior(df, api_key=api__key):
    """
    Toma un DataFrame con una columna 'url' y devuelve un DataFrame con tres columnas adicionales de tags.

    Parameters:
    df (pd.DataFrame): DataFrame con una columna 'url' que contiene las URLs de los productos.
    api_key (str): Clave de API de Anthropic.

    Returns:
    pd.DataFrame: DataFrame con tres columnas de tags agregadas.
    """
    client = Anthropic(api_key=api_key)
    df_result = df.copy()
    
    # Agregar columnas para los tags
    tag_columns = [f'Tag_{i+1}' for i in range(3)]
    for col in tag_columns:
        df_result[col] = None
    
    for index, row in df.iterrows():
        image_url = row['image_url']
        product_description = row.get('description')  # Usar descripción si está disponible
        print(product_description)
        try:
            response = requests.get(image_url)
            image_data = BytesIO(response.content)
            base64_image = base64.b64encode(image_data.read()).decode('utf-8')

            message_content = f"""
            Analiza la imagen del producto y clasifícalo en tres categorías principales. Usa exclusivamente UNA palabra de cada lista.
            Descripción del producto: "{product_description}"
            
            ESTILO (elige una): Casual, Formal, Vintage, Elegante, Deportivo, Streetwear, Clásico, Minimalista, Bohemio, Moderno, Monocromático.
            CATEGORÍA PRINCIPAL (elige una): Joggers, Baggy, Cargo, Tailoring, Skater, Standard, Slim, Straight, Rasgado, Carrot, Skinny, Ajustado, Deportivo, Chándal.
            CATEGORÍA SECUNDARIA (elige una): Joggers, Baggy, Cargo, Tailoring, Skater, Standard, Slim, Straight, Rasgado, Carrot, Skinny, Ajustado, Deportivo, Chándal.

            Asegúrate de que la clasificación refleje fielmente la apariencia y descripción del producto, la cateogoria principal y la secundaria deben ser diferentes.
            EL FORMATO DE RESPUESTA DEBE SER ÚNICAMENTE: "ESTILO, CATEGORÍA PRINCIPAL, CATEGORÍA SECUNDARIA"
            """
            
            message = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=500,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": message_content},
                        {"type": "image", "source": {"type": "base64", "media_type": "image/jpeg", "data": base64_image}}
                    ]
                }]
            )
            
            tags_text = message.content[0].text if isinstance(message.content, list) else message.content
            tags = tags_text.replace('\n', ', ').split(', ')
            if len(tags) == 3:
                df_result.loc[index, tag_columns] = tags

        except Exception as e:
            print(f"Error procesando la imagen {image_url}: {e}")
        
        time.sleep(1)  # Evitar restricciones de la API
        
    return df_result