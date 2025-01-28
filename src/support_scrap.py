import re
import json
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

def process_and_extract_data_main(urls):
    """
    Procesa una lista de URLs utilizando Selenium, realiza scroll infinito, extrae datos con BeautifulSoup
    y devuelve un DataFrame consolidado con la información de productos.

    Parámetros:
        urls (list): Lista de URLs a procesar.

    Retorna:
        DataFrame: Un DataFrame de pandas con columnas de nombres de productos, enlaces, URLs de imágenes y precios.
    """
    # Configuración del driver
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')  # Desactiva el uso de la GPU
    chrome_options.add_argument('--no-sandbox')  # Evita el uso del sandbox (útil en servidores)
    chrome_options.add_argument('--disable-dev-shm-usage')  # Soluciona problemas de espacio en /dev/shm
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    all_data = []

    try:
        for url in tqdm(urls):
            try:
                driver.get(url)
                time.sleep(2)  # Esperar a que la página cargue

                # Aceptar cookies
                try:
                    boton_cookies = driver.find_element(By.XPATH, '//*[@id="onetrust-accept-btn-handler"]')
                    boton_cookies.click()
                    time.sleep(1)
                    print("Cookies aceptadas")
                except Exception:
                    print("No se encontró el botón de cookies o ya estaban aceptadas")

                # Scroll infinito gradual
                scroll_pause_time = 0.6
                scroll_increment = 400
                last_height = driver.execute_script("return window.scrollY")

                while True:
                    driver.execute_script(f"window.scrollBy(0, {scroll_increment});")
                    time.sleep(scroll_pause_time)
                    new_height = driver.execute_script("return window.scrollY")
                    if new_height == last_height:
                        break
                    last_height = new_height

                # Obtener el HTML completo después del scroll
                html_completo = driver.page_source
                soup = BeautifulSoup(html_completo, 'html.parser')

                # Inicializar listas para almacenar los datos
                product_names, product_links, image1_urls, image2_urls, product_prices = [], [], [], [], []

                products = soup.find_all('legacy-product')
                print(f"Se han encontrado {len(products)} productos en {url}")

                for product in products:
                    name = product.find('span', class_='product-name')
                    product_names.append(name.text.strip() if name else None)

                    link = product.find('a', class_='carousel-item-container')
                    product_links.append(link['href'] if link and 'href' in link.attrs else None)

                    images = product.find_all('img', class_='image-responsive')
                    image_urls = [img['src'] for img in images if 'src' in img.attrs]
                    image1_urls.append(image_urls[0] if len(image_urls) > 0 else None)
                    image2_urls.append(image_urls[1] if len(image_urls) > 1 else None)

                    price_div = product.find('div', class_='product-price--price')
                    if price_div:
                        raw_price = price_div.text.strip().replace("\xa0", "").replace("€", "").strip()
                        try:
                            transformed_price = float(raw_price.replace(",", "."))
                            product_prices.append(transformed_price)
                        except ValueError:
                            product_prices.append(None)
                    else:
                        product_prices.append(None)

                # Crear un DataFrame con los datos extraídos de esta URL
                df = pd.DataFrame({
                    'product_name': product_names,
                    'url': product_links,
                    'image1_url': image1_urls,
                    'image2_url': image2_urls,
                    'product_price': product_prices
                })
                all_data.append(df)

            except Exception as e:
                print(f"Error procesando la URL {url}: {e}")

    finally:
        driver.quit()  # Asegurarse de cerrar el driver al final

    # Concatenar todos los DataFrames en uno solo
    return pd.concat(all_data, ignore_index=True) if all_data else pd.DataFrame()

def process_urls_products(df):
    """
    Función para procesar las URLs de un DataFrame, extrayendo información de cada una.

    Args:
        df (pd.DataFrame): DataFrame que contiene una columna 'url' con las URLs a procesar.

    Returns:
        pd.DataFrame: DataFrame con los resultados del procesamiento de cada URL.
    """
    # Extraer el valor numérico de los precios
    def extract_numeric_price(price_text):
        if price_text:
            return float(re.sub(r'[^\d,]', '', price_text).replace(',', '.'))
        return None

    # Configuración de Selenium
    chrome_options = Options()
    chrome_options.add_argument('--disable-gpu')  # Desactiva el uso de la GPU
    chrome_options.add_argument('--no-sandbox')  # Evita el uso del sandbox (útil en servidores)
    chrome_options.add_argument('--disable-dev-shm-usage')  # Soluciona problemas de espacio en /dev/shm

    # Función para procesar una URL individual
    def process_url(row):
        url = row['url']
        result = {
            "url": url,
            "description": None,
            "sale_price": None,
            "old_price": None,
            "original_price": None,
            "current_price": None,
            "color": None,
            "image_url": None,
            "mpn": None,
            "reference_code": None,
            "category_id": None,
            "Stock Status": "In stock"
        }
        try:
            driver.get(url)
            # Esperar hasta que el color esté presente (máximo 5 segundos)
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, '.product-card-color-selector--popup-colors-color-name'))
            )
            # Espera adicional para asegurarse de que la página está completamente cargada
            WebDriverWait(driver, 3).until(
                lambda x: x.execute_script("return document.readyState === 'complete'")
            )

            # Extraer contenido HTML
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extraer precios
            sale_price = soup.select_one('.prices .sale .number')
            old_price = soup.select_one('.prices .price-old .number')
            original_price = soup.select_one('.prices .price-original .number')
            single_price = soup.select_one('.price .number.hansolo')

            result['sale_price'] = extract_numeric_price(sale_price.text.strip()) if sale_price else None
            result['old_price'] = extract_numeric_price(old_price.text.strip()) if old_price else None
            result['original_price'] = extract_numeric_price(original_price.text.strip()) if original_price else None
            result['current_price'] = extract_numeric_price(single_price.text.strip()) if single_price else min(
                filter(None, [result['sale_price'], result['old_price'], result['original_price']]), default=None
            )

            # Extraer color
            color_element = soup.select_one('.product-card-color-selector--popup-colors-color-name')
            result['color'] = color_element.text.strip() if color_element else None

            # Extraer descripción y MPN
            json_ld = soup.find("script", type="application/ld+json")
            if json_ld:
                product_data = json.loads(json_ld.string)
                result['description'] = product_data.get("description", None)
                result['mpn'] = product_data.get("mpn", None)

            # Extraer datos del script JavaScript
            script_js = soup.find("script", text=re.compile("inditex.iParams"))
            if script_js:
                script_text = script_js.string
                mfname_match = re.search(r'mfname":\["(\d+)"\]', script_text)
                category_id_match = re.search(r'categoryId":\["(\d+)"\]', script_text)

                result['reference_code'] = mfname_match.group(1) if mfname_match else None
                result['category_id'] = category_id_match.group(1) if category_id_match else None

            # Extraer URL de la imagen principal
            if not result['image_url']:
                image_element = soup.select_one('img')
                result['image_url'] = image_element['src'] if image_element and 'src' in image_element.attrs else None

        except Exception as e:
            print(f"Error procesando la URL {url}: {e}")

        return result

    # Inicializar el navegador
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    try:
        # Procesar las filas del DataFrame
        rows = df.to_dict('records')
        with ThreadPoolExecutor(max_workers=1) as executor:
            results = list(tqdm(executor.map(process_url, rows), total=len(rows)))

    finally:
        driver.quit()

    # Convertir resultados en un DataFrame
    return pd.DataFrame(results)

def homogeneizar_color(color):
    """
    Homogeneiza la descripción de colores para clasificarlos en categorías estándar.

    Args:
        color (str): Cadena de texto que describe un color. Puede contener nombres específicos de colores, variaciones o matices.

    Returns:
        str: Categoría estandarizada del color.
    """
    # Convertir el color a una cadena en minúsculas para uniformidad
    color = str(color).lower()
    
    # Categorías estándar con posibles nombres asociados a cada una
    if any(c in color for c in ['blanco', 'hueso', 'crema', 'crudo']):
        return 'Blanco'  # Colores asociados a tonos claros o blancos
    elif any(c in color for c in ['negro', 'vigoré oscuro']):
        return 'Negro'  # Colores asociados a tonos oscuros o negro
    elif any(c in color for c in ['gris', 'vigoré', 'plomo']):
        return 'Gris'  # Colores asociados a tonos grises
    elif any(c in color for c in ['azul claro', 'azul flúor', 'indigo', 'celeste']):
        return 'Azul claro'  # Variaciones de azul en tonos claros
    elif any(c in color for c in ['azul', 'marino', 'indigo']):
        return 'Azul'  # Azul general o tonos oscuros como marino
    elif any(c in color for c in ['verde', 'menta', 'lima', 'botella', 'pistacho']):
        return 'Verde'  # Colores relacionados con tonos verdes
    elif any(c in color for c in ['beige', 'caqui', 'hielo', 'natural', 'piedra', 'tostado', 'arena']):
        return 'Marrón claro'  # Tonos claros asociados a marrón o beige
    elif any(c in color for c in ['marrón', 'caramelo', 'tabaco', 'chocolate', 'topo', 'tierra', 'coñac']):
        return 'Marrón'  # Tonos más oscuros de marrón
    elif any(c in color for c in ['rojo', 'granate', 'coral', 'burgundy', 'teja', 'burdeos']):
        return 'Rojo'  # Colores relacionados con tonos rojizos
    elif any(c in color for c in ['rosa', 'lila', 'berenjena', 'morado', 'malva']):
        return 'Rosa/Púrpura'  # Tonos entre rosa y púrpura
    elif any(c in color for c in ['amarillo', 'mostaza']):
        return 'Amarillo'  # Colores amarillos o mostaza
    elif any(c in color for c in ['naranja']):
        return 'Naranja'  # Colores asociados a naranja
    elif any(c in color for c in ['varios', 'rayas']):
        return 'Multicolor'  # Colores que representan combinaciones o patrones
    else:
        return 'Otros'  # Cualquier otro color no clasificado

    
def categorizar_ropa(product_name):
    product_name = str(product_name).lower()  # Convertir a minúsculas para uniformidad
    if any(p in product_name for p in ['pack']):
        return 'Pack'
    if any(p in product_name for p in ['camiseta','sudadera manga corta']):
        return 'Camiseta'
    if any(p in product_name for p in ['sudadera', 'hoodie']):
        return 'Sudadera'
    if any(p in product_name for p in ['polo']):
        return 'Polo'
    elif any(p in product_name for p in ['sobrecamisa']):
        return 'Sobrecamisa'
    elif any(p in product_name for p in ['camisa']):
        return 'Camisa'
    elif any(p in product_name for p in ['pantalón', 'pantalones', 'jeans', 'vaqueros']):
        return 'Pantalón'
    elif any(p in product_name for p in ['jersey']):
        return 'Jersey'
    elif any(p in product_name for p in ['zapato', 'botas', 'sandalias', 'calzado']):
        return 'Calzado'
    elif any(p in product_name for p in ['accesorio', 'gorra', 'bufanda', 'cinturón', 'bolso']):
        return 'Accesorio'
    else:
        return 'Otros'