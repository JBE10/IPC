import requests
from bs4 import BeautifulSoup
import re
from utils import limpiar_precio
from config import HEADERS

def obtener_precio_dia(codigo):
    """Obtiene el precio de un producto de Día usando su código."""
    try:
        api_url = f"https://diaonline.supermercadosdia.com.ar/api/catalog_system/pub/products/search?fq=productId:{codigo}"
        
        print(f"Consultando API para producto ID: {codigo}")
        response = requests.get(api_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        if data and len(data) > 0:
            price = data[0].get('items', [{}])[0].get('sellers', [{}])[0].get('commertialOffer', {}).get('Price')
            if price is not None:
                return float(price)
        
        print(f"No se encontró el precio para el código: {codigo}")
        return None
    except Exception as e:
        print(f"Error al obtener el precio: {e}")
        return None

def obtener_precio_disco(url):
    """Obtiene el precio de un producto de Disco."""
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
    """Obtiene el precio de un producto de Coto."""
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
    """Obtiene el precio de un producto de Jumbo."""
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