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
    validar_division,
    calcular_variacion_semanal,
    calcular_variacion_mensual,
    limpiar_precio
)
from scrapers import (
    obtener_precio_dia,
    obtener_precio_disco,
    obtener_precio_coto,
    obtener_precio_jumbo
)

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
                    if len(partes) >= 4:  # código, nombre, categoría, cantidad mensual
                        codigo, nombre, division, cantidad = partes
                        division = division.strip()
                        try:
                            cantidad = float(cantidad.strip())
                        except ValueError:
                            print(f"Advertencia: Cantidad mensual inválida para producto '{nombre.strip()}'. Se usa 1 por defecto.")
                            cantidad = 1.0
                        
                        division = validar_division(division)
                        
                        productos.append({
                            "codigo": codigo.strip(),
                            "nombre": nombre.strip(),
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
        precio = obtener_precio_dia(producto["codigo"])
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

def generar_resumen(precios, precios_por_division, cantidades_por_division, total, df_productos, productos):
    """Genera el resumen de precios y variaciones de la canasta básica de alimentos."""
    resumen = []
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M')
    fecha_ayer = (datetime.now() - pd.Timedelta(days=1)).strftime('%Y-%m-%d')
    
    resumen.append(f"Fecha: {fecha_actual}")
    resumen.append("\nPrecios individuales actuales (considerando cantidades mensuales):")
    for nombre_prod, precio_total_prod in precios.items():
        resumen.append(f"- {nombre_prod}: ${precio_total_prod:.2f}")
    
    resumen.append(f"\nValor total actual de la canasta (productos encontrados hoy): ${total:.2f}")
    resumen.append(f"Cantidad de productos con precio hoy: {len(precios)}")
    
    # Definir divisiones de alimentos básicos
    divisiones_alimentos = [
        "Alimentos y bebidas no alcohólicas",
        "Pan y cereales",
        "Panificados",
        "Almacén",
        "Frescos",
        "Bebidas"
    ]
    
    resumen.append("\nIPC por División (variación diaria comparable):")
    ipc_divisiones = {}
    total_valor_actual_canasta_alimentos_comparable = 0
    total_valor_anterior_canasta_alimentos_comparable = 0
    
    # Filtrar los productos de la canasta que pertenecen a las divisiones de alimentos
    productos_de_alimentos_config = [p for p in productos if p["division"] in divisiones_alimentos]
    
    for division_cfg, peso_config_division in DIVISIONES_IPC.items():
        if division_cfg not in divisiones_alimentos:
            continue
            
        valor_actual_division_comparable = 0
        valor_anterior_division_comparable = 0
        productos_contados_en_division = 0
        
        for producto_canasta in productos_de_alimentos_config:
            if producto_canasta["division"] == division_cfg:
                nombre_producto = producto_canasta["nombre"]
                cantidad_mensual = producto_canasta["cantidad_mensual"]
                
                # El precio actual ya está ponderado por cantidad_mensual en el diccionario 'precios'
                precio_total_actual_producto = precios.get(nombre_producto)
                
                # Buscar precio unitario del día anterior en el histórico df_productos
                producto_ayer_df = df_productos[
                    (df_productos["Producto"] == nombre_producto) & 
                    (df_productos["Fecha"].str.startswith(fecha_ayer))
                ] if not df_productos.empty else pd.DataFrame()
                
                if precio_total_actual_producto is not None and not producto_ayer_df.empty:
                    precio_unitario_ayer = producto_ayer_df.iloc[0]["Precio"]
                    
                    if pd.notna(precio_unitario_ayer):
                        precio_total_anterior_producto = precio_unitario_ayer * cantidad_mensual
                        
                        valor_actual_division_comparable += precio_total_actual_producto
                        valor_anterior_division_comparable += precio_total_anterior_producto
                        productos_contados_en_division += 1
        
        if productos_contados_en_division > 0 and valor_anterior_division_comparable > 0:
            variacion_division_comparable = valor_actual_division_comparable - valor_anterior_division_comparable
            porcentaje_division_comparable = (variacion_division_comparable / valor_anterior_division_comparable) * 100
            ipc_divisiones[division_cfg] = porcentaje_division_comparable
            signo = "+" if variacion_division_comparable >= 0 else ""
            resumen.append(f"- {division_cfg}: {signo}{porcentaje_division_comparable:.2f}% (sobre {productos_contados_en_division} prod. comparables)")
        else:
            ipc_divisiones[division_cfg] = 0.0
            resumen.append(f"- {division_cfg}: No hay datos suficientes para comparación diaria.")
        
        total_valor_actual_canasta_alimentos_comparable += valor_actual_division_comparable
        total_valor_anterior_canasta_alimentos_comparable += valor_anterior_division_comparable
    
    # Calcular IPC general basado solo en el conjunto de productos comparables
    ipc_general_final_a_guardar = 0.0
    if total_valor_anterior_canasta_alimentos_comparable > 0:
        variacion_total_directa_comparable = total_valor_actual_canasta_alimentos_comparable - total_valor_anterior_canasta_alimentos_comparable
        ipc_general_final_a_guardar = (variacion_total_directa_comparable / total_valor_anterior_canasta_alimentos_comparable) * 100
        resumen.append(f"\nIPC General Canasta Alimentos (Variación Diaria Directa Comparable): {ipc_general_final_a_guardar:+.2f}%")
        resumen.append(f"  Valor Actual Canasta Comparable: ${total_valor_actual_canasta_alimentos_comparable:.2f}")
        resumen.append(f"  Valor Anterior Canasta Comparable: ${total_valor_anterior_canasta_alimentos_comparable:.2f}")
    else:
        resumen.append("\nIPC General Canasta Alimentos (Variación Diaria Directa Comparable): No hay suficientes datos comparables para ayer.")
    
    return resumen, ipc_divisiones, ipc_general_final_a_guardar

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
    """Función principal del script."""
    # Cargar productos
    productos = cargar_productos()
    
    # Obtener precios actuales
    precios, precios_por_division, cantidades_por_division, total = obtener_precios(productos)
    
    if precios:
        # Verificar si es el primer día del mes
        if es_primer_dia_del_mes():
            print("\nEs el primer día del mes. Creando nuevos archivos CSV...")
            df_resumen, df_divisiones, df_productos = crear_nuevo_mes_csv()
        else:
            # Obtener DataFrames existentes
            df_resumen, df_divisiones, df_productos = obtener_ultimos_csvs()
        
        # Generar resumen
        resumen, ipc_divisiones, ipc_general = generar_resumen(
            precios, precios_por_division, cantidades_por_division, total, df_productos, productos
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
        
        # Calcular variación semanal
        try:
            # Calcular variación semanal
            variaciones_semanales = calcular_variacion_semanal(df_productos)
            
            # Guardar variaciones semanales
            variaciones_semanales.to_csv(f"variaciones_semanales_{datetime.now().strftime('%Y%m')}.csv", index=False)
            
            # Mostrar resumen de variaciones semanales
            print("\nVariaciones semanales promedio:")
            print("=" * 80)
            for _, row in variaciones_semanales.iterrows():
                print(f"\nProducto: {row['Producto']}")
                print(f"Semana {row['Semana_Actual']} del {row['Año_Actual']}")
                print(f"Precio promedio actual: ${row['Precio_Promedio_Actual']:.2f}")
                print(f"Precio promedio anterior: ${row['Precio_Promedio_Anterior']:.2f}")
                print(f"Variación: ${row['Variacion']:.2f} ({row['Porcentaje']:.2f}%)")
                print("-" * 80)
                
        except Exception as e:
            print(f"\nError al calcular variaciones semanales: {e}")
            print("Se necesitan al menos dos semanas de datos.")
            
        # Calcular variación mensual
        try:
            # Calcular variación mensual
            variaciones_mensuales = calcular_variacion_mensual(df_productos)
            
            # Guardar variaciones mensuales
            variaciones_mensuales.to_csv(f"variaciones_mensuales_{datetime.now().strftime('%Y%m')}.csv", index=False)
            
            # Mostrar resumen de variaciones mensuales
            print("\nVariaciones mensuales de la canasta básica de alimentos:")
            print("=" * 80)
            
            if not variaciones_mensuales.empty:
                # Para el resumen en texto, calculamos la variación ponderada por división
                # Necesitamos las cantidades mensuales de 'productos' (cargados de mi_carrito.txt)
                map_producto_cantidad = {p["nombre"]: p["cantidad_mensual"] for p in productos}

                variaciones_mensuales['Costo_Primer_Dia_Mes'] = variaciones_mensuales.apply(
                    lambda row: row['Precio_Primer_Dia'] * map_producto_cantidad.get(row['Producto'], 0), axis=1
                )
                variaciones_mensuales['Costo_Ultimo_Dia_Mes'] = variaciones_mensuales.apply(
                    lambda row: row['Precio_Ultimo_Dia'] * map_producto_cantidad.get(row['Producto'], 0), axis=1
                )

                resumen_mensual_division_costos = variaciones_mensuales.groupby('Division').agg(
                    Total_Costo_Primer_Dia_Mes=('Costo_Primer_Dia_Mes', 'sum'),
                    Total_Costo_Ultimo_Dia_Mes=('Costo_Ultimo_Dia_Mes', 'sum')
                ).reset_index()

                resumen_mensual_division_costos['Variacion_Absoluta_Division_Mes'] = resumen_mensual_division_costos['Total_Costo_Ultimo_Dia_Mes'] - resumen_mensual_division_costos['Total_Costo_Primer_Dia_Mes']
                
                def calcular_porcentaje_seguro(row):
                    if row['Total_Costo_Primer_Dia_Mes'] != 0:
                        return (row['Variacion_Absoluta_Division_Mes'] / row['Total_Costo_Primer_Dia_Mes']) * 100
                    return 0.0

                resumen_mensual_division_costos['Porcentaje_Ponderado_Division_Mes'] = resumen_mensual_division_costos.apply(calcular_porcentaje_seguro, axis=1)
                
                resumen.append("\nVariaciones Mensuales Ponderadas por División (Intra-Mes: Fin vs Inicio):")
                for _, row_div in resumen_mensual_division_costos.iterrows():
                    signo_porc = "+" if row_div['Porcentaje_Ponderado_Division_Mes'] >= 0 else ""
                    signo_abs = "+" if row_div['Variacion_Absoluta_Division_Mes'] >= 0 else ""
                    resumen.append(f"\n- División: {row_div['Division']}")
                    resumen.append(f"  Variación ponderada: {signo_porc}{row_div['Porcentaje_Ponderado_Division_Mes']:.2f}%")
                    resumen.append(f"  Variación absoluta (costo canasta división): {signo_abs}${row_div['Variacion_Absoluta_Division_Mes']:.2f}")
            else:
                resumen.append("\nNo hay suficientes datos para el resumen de variación mensual por división este mes.")
                
        except Exception as e:
            print(f"\nError al calcular o resumir variaciones mensuales: {e}")
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
    print(f"- variaciones_semanales_{datetime.now().strftime('%Y%m')}.csv")
    print(f"- variaciones_mensuales_{datetime.now().strftime('%Y%m')}.csv")

if __name__ == "__main__":
    main()

    