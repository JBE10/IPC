import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import os
import json
import csv

# --- Función para Limpiar y Convertir Precios ---
def limpiar_precio(texto_precio):
    if not texto_precio:
        return None
    # Quitar símbolo de moneda, puntos de miles y espacios (incluyendo \xa0)
    limpio = texto_precio.replace("$", "").replace(".", "").replace("\xa0", "").replace("\u202f", "").replace(" ", "").strip()
    # Reemplazar coma decimal por punto decimal
    limpio = limpio.replace(",", ".")
    try:
        return float(limpio)
    except ValueError:
        print(f"Advertencia: No se pudo convertir a número: '{texto_precio}' -> '{limpio}'")
        return None

# --- Headers mejorados para simular un navegador real ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0'
}

def obtener_precio_dia(url):
    try:
        # Extraer el ID del producto de la URL
        # El formato es: https://diaonline.supermercadosdia.com.ar/nombre-producto-ID/p
        product_id = None
        
        # Intentar extraer el ID del final de la URL antes de /p
        if '/p' in url:
            url_base = url.split('/p')[0]
            segments = url_base.split('/')
            if segments:
                last_segment = segments[-1]
                # Buscar un número al final del segmento
                match = re.search(r'(\d+)$', last_segment)
                if match:
                    product_id = match.group(1)
        
        if not product_id:
            print(f"No se pudo extraer el ID del producto de la URL: {url}")
            return None
            
        # Construir la URL de la API
        api_url = f"https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?fq=productId:{product_id}"
        
        print(f"Consultando API para producto ID: {product_id}")
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        # Parsear la respuesta JSON
        data = response.json()
        
        if data and len(data) > 0:
            # Obtener el precio del primer producto encontrado
            price = data[0].get('items', [{}])[0].get('sellers', [{}])[0].get('commertialOffer', {}).get('Price')
            if price is not None:
                return float(price)
        
        print(f"No se encontró el precio para la URL: {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error de conexión al obtener el precio: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error al decodificar la respuesta JSON: {e}")
        return None
    except Exception as e:
        print(f"Error inesperado al obtener el precio: {e}")
        return None

def obtener_precio_disco(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Intentar diferentes selectores para Disco
        selectores = [
            'div#priceContainer',
            'div.discoargentina-store-theme-1dCOMij_MzTzZOCohX1K7w',
            'span.vtex-store-components-3-x-sellingPriceValue'
        ]
        
        for selector in selectores:
            elemento_precio = soup.select_one(selector)
            if elemento_precio:
                return limpiar_precio(elemento_precio.text)
        
        print(f"No se encontró el elemento del precio en Disco para la URL: {url}")
        return None
    except Exception as e:
        print(f"Error al obtener la página de Disco: {e}")
        return None

def obtener_precio_coto(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Intentar diferentes selectores para Coto
        selectores = [
            'var.price.h3.ng-star-inserted',
            'span.atg_store_productPrice',
            'span.textPrecio'
        ]
        
        for selector in selectores:
            elemento_precio = soup.select_one(selector)
            if elemento_precio:
                return limpiar_precio(elemento_precio.text)
        
        print(f"No se encontró el elemento del precio en Coto para la URL: {url}")
        return None
    except Exception as e:
        print(f"Error al obtener la página de Coto: {e}")
        return None

def obtener_precio_jumbo(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Intentar diferentes selectores para Jumbo
        selectores = [
            'div.jumboargentinaio-store-theme-1dCOMij_MzTzZOCohX1K7w',
            'span.vtex-store-components-3-x-sellingPriceValue',
            'div.product-price'
        ]
        
        for selector in selectores:
            elemento_precio = soup.select_one(selector)
            if elemento_precio:
                return limpiar_precio(elemento_precio.text)
        
        print(f"No se encontró el elemento del precio en Jumbo para la URL: {url}")
        return None
    except Exception as e:
        print(f"Error al obtener la página de Jumbo: {e}")
        return None

# --- Lógica Principal ---
if __name__ == "__main__":
    # Leer productos desde mi_carrito.txt
    productos = []
    if os.path.exists("mi_carrito.txt"):
        with open("mi_carrito.txt", "r", encoding="utf-8") as f:
            for linea in f:
                if linea.strip():
                    url, nombre = linea.strip().split(';')
                    productos.append({
                        "nombre": nombre.strip(),
                        "url": url.strip()
                    })
    else:
        print("No se encontró el archivo mi_carrito.txt")
        exit(1)

    precios = {}
    resumen = []
    total = 0
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M')

    print(f"Obteniendo precios de la canasta personalizada...\n")
    print(f"Fecha: {fecha_actual}\n")

    for producto in productos:
        precio = obtener_precio_dia(producto["url"])
        if precio is not None:
            precios[producto["nombre"]] = precio
            total += precio
            print(f"{producto['nombre']}: ${precio:.2f}")
        else:
            print(f"{producto['nombre']}: No disponible")
        time.sleep(2)  # Esperar 2 segundos entre peticiones

    print("\n--- Resumen ---")
    if precios:
        resumen.append(f"Fecha: {fecha_actual}")
        resumen.append("\nPrecios individuales:")
        for producto, precio in precios.items():
            resumen.append(f"- {producto}: ${precio:.2f}")
        
        resumen.append(f"\nTotal de la canasta: ${total:.2f}")
        resumen.append(f"Cantidad de productos: {len(precios)}")
        
        # Imprimir el resumen
        for linea in resumen:
            print(linea)
    else:
        resumen.append("No se pudo obtener el precio de ningún producto.")
        print("No se pudo obtener el precio de ningún producto.")

    # Guardar resultados en un archivo txt
    nombre_archivo = f"canasta_personalizada_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        for linea in resumen:
            f.write(linea + "\n")

    # Guardar en CSV para seguimiento de precios
    csv_filename = "seguimiento_precios.csv"
    file_exists = os.path.exists(csv_filename)
    
    with open(csv_filename, "a", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Si el archivo no existe, escribir los encabezados
        if not file_exists:
            headers = ['Fecha'] + [producto["nombre"] for producto in productos] + ['Total']
            writer.writerow(headers)
        
        # Escribir los precios del día
        row = [fecha_actual]
        for producto in productos:
            precio = precios.get(producto["nombre"], "N/A")
            row.append(precio if precio != "N/A" else "")
        row.append(total)
        writer.writerow(row)

    print(f"\nResultados guardados en {nombre_archivo} y {csv_filename}")