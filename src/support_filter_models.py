from transformers import pipeline
from ultralytics import YOLO
from PIL import Image
import numpy as np
import pandas as pd
import requests
import time

def is_white_background(image_url, border_size=10, threshold=220, max_retries=3, retry_delay=5):
    """Determina si el fondo de una imagen es blanco verificando los bordes, con reintentos en caso de fallo."""
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(image_url, stream=True, timeout=10)

            # Verificar si la solicitud fue exitosa
            if response.status_code != 200:
                raise ValueError(f"Error en URL: {image_url} (Código {response.status_code})")

            # Verificar si el contenido es una imagen
            content_type = response.headers.get("Content-Type", "")
            if not content_type.startswith("image"):
                raise ValueError(f"Error en URL: {image_url} (No es una imagen)")

            # Abrir la imagen
            image = Image.open(response.raw).convert("RGB")

            # Convertir la imagen en un array de píxeles
            img_array = np.array(image)

            # Extraer bordes (superior, inferior, izquierdo y derecho)
            top = img_array[:border_size, :, :].reshape(-1, 3)
            bottom = img_array[-border_size:, :, :].reshape(-1, 3)
            left = img_array[:, :border_size, :].reshape(-1, 3)
            right = img_array[:, -border_size:, :].reshape(-1, 3)

            # Concatenar los bordes en un solo array de píxeles
            border_pixels = np.vstack([top, bottom, left, right])

            # Calcular el color promedio
            avg_color = border_pixels.mean(axis=0)

            # Verificar si el fondo es blanco
            is_white = np.all(avg_color >= threshold)

            return "Blanco" if is_white else "Otro color"
        
        except Exception as e:
            print(f"Intento {retries + 1} fallido: {e}")
            retries += 1
            time.sleep(retry_delay)
    
    return f"Error persistente en URL: {image_url}"

    
classifier = pipeline("image-classification", model="facebook/dino-vitb16")

# Cargar modelo YOLOv8 preentrenado para detección de objetos
model = YOLO("yolov8n.pt")

def classify_image(image_url):
    """Detecta si la imagen contiene una persona o un pantalón."""
    response = requests.get(image_url, stream=True, timeout=10)
    if response.status_code != 200:
        return f"Error en URL: {image_url}"

    image = Image.open(response.raw).convert("RGB")

    # Ejecutar detección de objetos
    results = model(image)

    # Obtener clases detectadas (person = 0, pants = puede ser "jeans" o similar)
    detected_classes = [model.names[int(box.cls)] for box in results[0].boxes]

    if "person" in detected_classes:
        return "Modelo"
    elif "jeans" in detected_classes or "pants" in detected_classes:
        return "Pantalón"
    else:
        return "No identificado"