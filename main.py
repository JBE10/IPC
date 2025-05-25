import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime

# --- Función para Limpiar y Convertir Precios ---
def limpiar_precio(texto_precio):
    if not texto_precio:
        return None
    # Quitar símbolo de moneda, puntos de miles y espacios
    limpio = texto_precio.replace("$", "").replace(".", "").strip()
    # Reemplazar coma decimal por punto decimal
    limpio = limpio.replace(",", ".")
    try:
        return float(limpio)
    except ValueError:
        print(f"Advertencia: No se pudo convertir a número: '{texto_precio}'")
        return None

# --- Headers mejorados para simular un navegador real ---
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Cache-Control': 'max-age=0'
}

def obtener_precio_dia(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Intentar diferentes selectores para DIA
        selectores = [
            'span.diaio-store-5-x-sellingPriceValue',
            'span.vtex-product-price-1-x-sellingPriceValue',
            'span.price-value'
        ]
        
        for selector in selectores:
            elemento_precio = soup.select_one(selector)
            if elemento_precio:
                return limpiar_precio(elemento_precio.text)
        
        print(f"No se encontró el elemento del precio para la URL: {url}")
        return None
    except Exception as e:
        print(f"Error al obtener la página: {e}")
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
    # Canasta básica con productos de DIA
    canasta_basica = {
        "Leche La Serenísima Protein 1Lt": "https://diaonline.supermercadosdia.com.ar/leche-descremada-la-serenisima-protein-1-lt-272382/p",
        "Arroz Gallo Oro 1kg": "https://diaonline.supermercadosdia.com.ar/arroz-gallo-oro-1-kg-272382/p",
        "Fideos Matarazzo Spaghetti 500g": "https://diaonline.supermercadosdia.com.ar/fideos-matarazzo-spaghetti-500-g-272382/p",
        "Aceite Cocinero 900ml": "https://diaonline.supermercadosdia.com.ar/aceite-cocinero-900-ml-272382/p",
        "Azúcar Ledesma 1kg": "https://diaonline.supermercadosdia.com.ar/azucar-ledesma-1-kg-272382/p",
        "Harina Pureza 1kg": "https://diaonline.supermercadosdia.com.ar/harina-pureza-1-kg-272382/p",
        "Yerba Nobleza Gaucha 1kg": "https://diaonline.supermercadosdia.com.ar/yerba-nobleza-gaucha-1-kg-272382/p",
        "Café La Virginia 500g": "https://diaonline.supermercadosdia.com.ar/cafe-la-virginia-500-g-272382/p",
        "Dulce de Leche La Serenísima 400g": "https://diaonline.supermercadosdia.com.ar/dulce-de-leche-la-serenisima-400-g-272382/p",
        "Manteca La Serenísima 200g": "https://diaonline.supermercadosdia.com.ar/manteca-la-serenisima-200-g-272382/p"
    }

    precios = {}
    resumen = []
    total = 0

    print(f"Obteniendo precios de la canasta básica en DIA...\n")
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")

    for producto, url in canasta_basica.items():
        precio = obtener_precio_dia(url)
        if precio is not None:
            precios[producto] = precio
            total += precio
            print(f"{producto}: ${precio:.2f}")
        time.sleep(2)  # Esperar 2 segundos entre peticiones

    print("\n--- Resumen ---")
    if precios:
        resumen.append(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        resumen.append("\nPrecios individuales:")
        for producto, precio in precios.items():
            resumen.append(f"- {producto}: ${precio:.2f}")
        
        resumen.append(f"\nTotal de la canasta básica: ${total:.2f}")
        resumen.append(f"Cantidad de productos: {len(precios)}")
        
        # Imprimir el resumen
        for linea in resumen:
            print(linea)
    else:
        resumen.append("No se pudo obtener el precio de ningún producto.")
        print("No se pudo obtener el precio de ningún producto.")

    # Guardar resultados en un archivo txt
    nombre_archivo = f"canasta_basica_dia_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        for linea in resumen:
            f.write(linea + "\n")