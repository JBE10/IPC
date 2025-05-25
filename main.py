import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime
import os
import json
import csv
import pandas as pd
import difflib
from statistics import mean

from config import DIVISIONES_IPC
from utils import (
    es_primer_dia_del_mes,
    crear_nuevo_mes_csv,
    obtener_ultimos_csvs,
    validar_division
)
from scrapers import (
    obtener_precio_dia,
    obtener_precio_disco,
    obtener_precio_coto,
    obtener_precio_jumbo
)

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

def cargar_productos():
    """Carga los productos desde el archivo mi_carrito.txt."""
    productos = []
    productos_ignorados = []
    
    if os.path.exists("mi_carrito.txt"):
        with open("mi_carrito.txt", "r", encoding="utf-8") as f:
            for linea in f:
                if linea.strip():
                    partes = linea.strip().split(';')
                    if len(partes) >= 4:  # URL, nombre, categoría, cantidad mensual
                        url, nombre, division, cantidad = partes
                        division = division.strip()
                        try:
                            cantidad = float(cantidad.strip())
                        except ValueError:
                            print(f"Advertencia: Cantidad mensual inválida para producto '{nombre.strip()}'. Se usa 1 por defecto.")
                            cantidad = 1.0
                        
                        division = validar_division(division)
                        
                        productos.append({
                            "nombre": nombre.strip(),
                            "url": url.strip(),
                            "division": division,
                            "cantidad_mensual": cantidad
                        })
                    else:
                        print(f"Advertencia: Formato incorrecto en línea: {linea}")
                        productos_ignorados.append(linea.strip())
    else:
        print("No se encontró el archivo mi_carrito.txt")
        exit(1)

    if productos_ignorados:
        print("\nProductos ignorados por formato incorrecto:")
        for p in productos_ignorados:
            print(f"- {p}")
            
    return productos

def obtener_precios(productos):
    """Obtiene los precios de todos los productos."""
    precios = {}
    precios_por_division = {division: [] for division in DIVISIONES_IPC.keys()}
    cantidades_por_division = {division: [] for division in DIVISIONES_IPC.keys()}
    total = 0
    
    print(f"Obteniendo precios de la canasta personalizada...\n")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")

    for producto in productos:
        precio = obtener_precio_dia(producto["url"])
        if precio is not None:
            precio_total = precio * producto["cantidad_mensual"]
            precios[producto["nombre"]] = precio_total
            total += precio_total
            if producto["division"] in precios_por_division:
                precios_por_division[producto["division"]].append(precio_total)
                cantidades_por_division[producto["division"]].append(producto["cantidad_mensual"])
            print(f"{producto['nombre']} (x{producto['cantidad_mensual']} unidades mensuales): ${precio_total:.2f} (${precio:.2f} c/u)")
        else:
            print(f"{producto['nombre']}: No disponible")
        time.sleep(2)  # Esperar 2 segundos entre peticiones
        
    return precios, precios_por_division, cantidades_por_division, total

def generar_resumen(precios, precios_por_division, cantidades_por_division, total, df_productos):
    """Genera el resumen de precios y variaciones."""
    resumen = []
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    resumen.append(f"Fecha: {fecha_actual}")
    resumen.append("\nPrecios individuales (considerando cantidades mensuales):")
    for producto, precio in precios.items():
        resumen.append(f"- {producto}: ${precio:.2f}")
    
    resumen.append(f"\nValor total de la canasta: ${total:.2f}")
    resumen.append(f"Cantidad de productos: {len(precios)}")
    
    # Calcular IPC por división
    resumen.append("\nIPC por División (variación diaria):")
    ipc_divisiones = {}
    for division, peso in DIVISIONES_IPC.items():
        precios_actuales = precios_por_division.get(division, [])
        cantidades_actuales = cantidades_por_division.get(division, [])
        if precios_actuales and cantidades_actuales:
            precios_anteriores = []
            cantidades_anteriores = []
            for producto in productos:
                if producto["division"] == division:
                    producto_anterior = df_productos[
                        (df_productos["Producto"] == producto["nombre"]) & 
                        (df_productos["Fecha"] == df_productos["Fecha"].max())
                    ] if not df_productos.empty else pd.DataFrame()
                    
                    if not producto_anterior.empty:
                        precio_anterior = producto_anterior.iloc[0]["Precio"]
                        if precio_anterior is not None:
                            precios_anteriores.append(precio_anterior)
                            cantidades_anteriores.append(producto["cantidad_mensual"])
            
            if precios_anteriores and cantidades_anteriores:
                precio_promedio_actual = sum(precios_actuales) / sum(cantidades_actuales)
                precio_promedio_anterior = sum(precios_anteriores) / sum(cantidades_anteriores)
                
                variacion_promedio = precio_promedio_actual - precio_promedio_anterior
                porcentaje = (variacion_promedio / precio_promedio_anterior) * 100
                ipc_divisiones[division] = porcentaje
                signo = "+" if variacion_promedio > 0 else ""
                resumen.append(f"- {division}: {signo}{porcentaje:.1f}% (Peso: {peso*100:.1f}%)")
    
    # Calcular IPC general ponderado
    ipc_general = sum(ipc * peso for ipc, peso in zip(ipc_divisiones.values(), DIVISIONES_IPC.values()))
    resumen.append(f"\nIPC General (variación diaria): {ipc_general:.1f}%")
    
    return resumen, ipc_divisiones, ipc_general

def guardar_datos(fecha_actual, total, ipc_general, ipc_divisiones, precios_por_division, precios, productos):
    """Guarda los datos en los archivos CSV."""
    # Obtener o crear los DataFrames
    df_resumen, df_divisiones, df_productos = obtener_ultimos_csvs()
    
    # 1. Guardar resumen general
    nueva_fila_resumen = {
        "Fecha": fecha_actual,
        "Total_Canasta": total,
        "IPC_General": ipc_general
    }
    
    # Calcular variaciones del total
    if not df_resumen.empty:
        total_anterior = df_resumen.iloc[-1]["Total_Canasta"]
        variacion_total = total - total_anterior
        porcentaje_total = (variacion_total / total_anterior) * 100
        nueva_fila_resumen["Variacion_Total"] = variacion_total
        nueva_fila_resumen["Porcentaje_Total"] = porcentaje_total
    else:
        nueva_fila_resumen["Variacion_Total"] = None
        nueva_fila_resumen["Porcentaje_Total"] = None
    
    df_resumen = pd.concat([df_resumen, pd.DataFrame([nueva_fila_resumen])], ignore_index=True)
    
    # 2. Guardar datos por división
    filas_divisiones = []
    for division in DIVISIONES_IPC.keys():
        total_division = sum(precios_por_division.get(division, []))
        nueva_fila_division = {
            "Fecha": fecha_actual,
            "Division": division,
            "Total": total_division,
            "IPC": ipc_divisiones.get(division, 0)
        }
        
        if not df_divisiones.empty:
            division_anterior = df_divisiones[
                (df_divisiones["Division"] == division) & 
                (df_divisiones["Fecha"] == df_divisiones["Fecha"].max())
            ]
            if not division_anterior.empty:
                total_anterior = division_anterior.iloc[0]["Total"]
                variacion = total_division - total_anterior
                porcentaje = (variacion / total_anterior) * 100
                nueva_fila_division["Variacion"] = variacion
                nueva_fila_division["Porcentaje"] = porcentaje
            else:
                nueva_fila_division["Variacion"] = None
                nueva_fila_division["Porcentaje"] = None
        else:
            nueva_fila_division["Variacion"] = None
            nueva_fila_division["Porcentaje"] = None
        
        filas_divisiones.append(nueva_fila_division)
    
    df_divisiones = pd.concat([df_divisiones, pd.DataFrame(filas_divisiones)], ignore_index=True)
    
    # 3. Guardar datos por producto
    filas_productos = []
    for producto in productos:
        nombre = producto["nombre"]
        precio_actual = precios.get(nombre)
        nueva_fila_producto = {
            "Fecha": fecha_actual,
            "Producto": nombre,
            "Division": producto["division"],
            "Precio": precio_actual
        }
        
        if not df_productos.empty:
            producto_anterior = df_productos[
                (df_productos["Producto"] == nombre) & 
                (df_productos["Fecha"] == df_productos["Fecha"].max())
            ]
            if not producto_anterior.empty:
                precio_anterior = producto_anterior.iloc[0]["Precio"]
                if precio_anterior is not None and precio_actual is not None:
                    variacion = precio_actual - precio_anterior
                    porcentaje = (variacion / precio_anterior) * 100
                    nueva_fila_producto["Variacion"] = variacion
                    nueva_fila_producto["Porcentaje"] = porcentaje
                else:
                    nueva_fila_producto["Variacion"] = None
                    nueva_fila_producto["Porcentaje"] = None
            else:
                nueva_fila_producto["Variacion"] = None
                nueva_fila_producto["Porcentaje"] = None
        else:
            nueva_fila_producto["Variacion"] = None
            nueva_fila_producto["Porcentaje"] = None
        
        filas_productos.append(nueva_fila_producto)
    
    df_productos = pd.concat([df_productos, pd.DataFrame(filas_productos)], ignore_index=True)
    
    # Guardar todos los DataFrames
    df_resumen.to_csv(f"resumen_{datetime.now().strftime('%Y%m')}.csv", index=False)
    df_divisiones.to_csv(f"divisiones_{datetime.now().strftime('%Y%m')}.csv", index=False)
    df_productos.to_csv(f"productos_{datetime.now().strftime('%Y%m')}.csv", index=False)
    
    return df_resumen, df_divisiones, df_productos

def main():
    """Función principal del programa."""
    # Cargar productos
    productos = cargar_productos()
    
    # Obtener precios
    precios, precios_por_division, cantidades_por_division, total = obtener_precios(productos)
    
    if precios:
        # Obtener DataFrames
        df_resumen, df_divisiones, df_productos = obtener_ultimos_csvs()
        
        # Generar resumen
        resumen, ipc_divisiones, ipc_general = generar_resumen(
            precios, precios_por_division, cantidades_por_division, total, df_productos
        )
        
        # Guardar datos
        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M')
        df_resumen, df_divisiones, df_productos = guardar_datos(
            fecha_actual, total, ipc_general, ipc_divisiones,
            precios_por_division, precios, productos
        )
        
        # Actualizar el resumen con las variaciones por división
        resumen.append("\nVariaciones por división:")
        for division in DIVISIONES_IPC.keys():
            total_division = sum(precios_por_division.get(division, []))
            variacion = df_divisiones.iloc[-1]["Variacion"] if not df_divisiones.empty else None
            porcentaje = df_divisiones.iloc[-1]["Porcentaje"] if not df_divisiones.empty else None
            ipc = df_divisiones.iloc[-1]["IPC"] if not df_divisiones.empty else None
            
            if variacion is not None and porcentaje is not None:
                signo = "+" if variacion > 0 else ""
                resumen.append(f"- {division}:")
                resumen.append(f"  Total: ${total_division:.2f}")
                resumen.append(f"  Variación: {signo}${variacion:.2f} ({signo}{porcentaje:.1f}%)")
                resumen.append(f"  IPC: {signo}{ipc:.1f}%")
        
        print("\n".join(resumen))
    else:
        print("No se pudo obtener el precio de ningún producto.")

    # Guardar resultados en un archivo txt
    nombre_archivo = f"canasta_personalizada_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    with open(nombre_archivo, "w", encoding="utf-8") as f:
        for linea in resumen:
            f.write(linea + "\n")

    print(f"\nResultados guardados en:")
    print(f"- {nombre_archivo}")
    print(f"- resumen_{datetime.now().strftime('%Y%m')}.csv")
    print(f"- divisiones_{datetime.now().strftime('%Y%m')}.csv")
    print(f"- productos_{datetime.now().strftime('%Y%m')}.csv")

if __name__ == "__main__":
    main()