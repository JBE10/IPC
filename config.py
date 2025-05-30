# Definición de divisiones del IPC y sus pesos
DIVISIONES_IPC = {
    # Alimentos y bebidas
    "Alimentos y bebidas no alcohólicas": 0.20,
    "Pan y cereales": 0.20,
    "Bebidas alcohólicas y tabaco": 0.027,
    
    # Categorías de supermercado
    "Panificados": 0.05,
    "Almacén": 0.15,
    "Frescos": 0.20,
    "Bebidas": 0.05,
    
    # Otras categorías
    "Prendas de vestir y calzado": 0.057,
    "Vivienda, agua, electricidad, gas y otros combustibles": 0.15,
    "Muebles, artículos para el hogar y para la conservación ordinaria del hogar": 0.05,
    "Salud": 0.10,
    "Transporte": 0.10,
    "Comunicación": 0.05,
    "Recreación y cultura": 0.05,
    "Educación": 0.05,
    "Restaurantes y hoteles": 0.05,
    "Bienes y servicios diversos": 0.05
}

# Headers para las peticiones HTTP
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Accept': 'application/json',
    'Accept-Language': 'es-AR,es;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0'
} 