![Logo del Proyecto](https://raw.githubusercontent.com/SrAlcast/Estylizer_project/refs/heads/main/src/Logo_Estylizer_1.png)

---

## 📖 Descripción del Proyecto

**Estylizer** es una aplicación inteligente diseñada para transformar la experiencia de compra de moda masculina. Mediante el uso de **Inteligencia Artificial** y **procesamiento de imágenes**, la plataforma recomienda outfits personalizados según las preferencias de estilo, colores y presupuesto del usuario.

Inicialmente, Estylizer se enfoca en moda masculina de **Pull&Bear** y está en proceso de expandirse a otras marcas del grupo **Inditex**. Además, se contempla la automatización del proceso de actualización de productos y la integración con plataformas de e-commerce.

## 🗂️ Estructura del Proyecto

```
├── src/                 # Código fuente
├── Streamlit/          # Archivos de la aplicación en Streamlit
├── notebooks/          # Jupyter Notebooks de análisis, scrapeo, tageo y actualización de datos
├── .devcontainer/      # Configuración para entornos de desarrollo en contenedores
├── results/            # Gráficos y reportes de resultados
├── README.md           # Descripción del proyecto
```

## 🛠️ Instalación y Requisitos

Este proyecto usa **Python 3.8+** y requiere las siguientes librerías:

- [pandas](https://pandas.pydata.org/)
- [numpy](https://numpy.org/)
- [streamlit](https://streamlit.io/)
- [pymongo](https://pymongo.readthedocs.io/)
- [selenium](https://www.selenium.dev/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [sklearn](https://scikit-learn.org/)
- [Anthropic](https://console.anthropic.com/)
- [YOLO](https://github.com/ultralytics/yolov5)
- [transformers](https://huggingface.co/transformers/)

Para instalar todas las dependencias, ejecuta:

```bash
pip install -r requirements.txt
```

## 🚀 Funcionamiento

1. **Selección de preferencias:** El usuario indica sus preferencias de estilo, colores y presupuesto.
2. **Procesamiento de datos:** Se realiza un filtrado de productos usando etiquetas generadas con IA y técnicas de procesamiento de lenguaje natural.
3. **Generación de recomendaciones:** Basado en similitud de características, se sugieren prendas compatibles.
4. **Interfaz interactiva:** El usuario visualiza sus opciones y ajusta las recomendaciones en tiempo real.

## 🌐 Enlace a la Aplicación

Prueba la versión funcional de **Estylizer** en Streamlit:

🔗 [Accede aquí](https://estylizer.streamlit.app/)

## 📊 Resultados y Conclusiones

- **Optimiza la experiencia de compra** reduciendo el tiempo de búsqueda de outfits.
- **Aumenta la conversión** de carritos abandonados en compras efectivas.
- **Fomenta la fidelización** mediante recomendaciones personalizadas.
- **Automatización de actualización de datos** mediante Jupyter Notebooks.
- **Integración con plataformas de e-commerce** para facilitar la compra directa desde Estylizer.

## 🔄 Próximos Pasos

- Ampliar la oferta de productos a **Zara y Bershka**.
- Expandir las recomendaciones a **moda femenina**.
- Implementar un sistema de **feedback post-compra** para mejorar la precisión del modelo.
- Incorporar más funcionalidades de análisis visual con **YOLO y modelos Transformer**.
- **Optimización del rendimiento** en la generación de recomendaciones y tiempos de consulta.
- **Evaluación de KPIs** como tasa de conversión y tiempo de permanencia.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar el proyecto, por favor abre un **Pull Request** o una **Issue**.

## ✒️ Autor

- **Alejandro Castro Varela** - [@SrAlcast](https://github.com/SrAlcast)

## 💬 Agradecimientos

A todos los colaboradores y testers que han apoyado el desarrollo de **Estylizer**. Este proyecto forma parte del Bootcamp de Data Science de **Hack(io) 2025**.

