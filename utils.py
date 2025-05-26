import re
from datetime import datetime
import pandas as pd
import os
import difflib
from config import DIVISIONES_IPC

def limpiar_precio(texto_precio):
    """Limpia y convierte un texto de precio a número."""
    if not texto_precio:
        return None
    # Quitar símbolo de moneda, puntos de miles y espacios
    limpio = texto_precio.replace("$", "").replace(".", "").replace("\xa0", "").replace("\u202f", "").replace(" ", "").strip()
    # Reemplazar coma decimal por punto decimal
    limpio = limpio.replace(",", ".")
    try:
        return float(limpio)
    except ValueError:
        print(f"Advertencia: No se pudo convertir a número: '{texto_precio}' -> '{limpio}'")
        return None

def es_primer_dia_del_mes():
    """Verifica si es el primer día del mes."""
    return datetime.now().day == 1

def crear_nuevo_mes_csv():
    """Crea los archivos CSV para un nuevo mes."""
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    # 1. Resumen general
    df_resumen = pd.DataFrame(columns=[
        'Fecha',
        'Total_Canasta',
        'Variacion_Total',
        'Porcentaje_Total',
        'IPC_General'
    ])
    
    # 2. Divisiones
    df_divisiones = pd.DataFrame(columns=[
        'Fecha',
        'Division',
        'Total',
        'Variacion',
        'Porcentaje',
        'IPC'
    ])
    
    # 3. Productos
    df_productos = pd.DataFrame(columns=[
        'Fecha',
        'Producto',
        'Division',
        'Precio',
        'Variacion',
        'Porcentaje'
    ])
    
    # Guardar los DataFrames en archivos separados
    df_resumen.to_csv(f"resumen_{datetime.now().strftime('%Y%m')}.csv", index=False)
    df_divisiones.to_csv(f"divisiones_{datetime.now().strftime('%Y%m')}.csv", index=False)
    df_productos.to_csv(f"productos_{datetime.now().strftime('%Y%m')}.csv", index=False)
    
    return df_resumen, df_divisiones, df_productos

def obtener_ultimos_csvs():
    """Obtiene los últimos archivos CSV del mes actual o crea nuevos si no existen."""
    mes_actual = datetime.now().strftime('%Y%m')
    
    # Cargar o crear los archivos
    if os.path.exists(f"resumen_{mes_actual}.csv"):
        df_resumen = pd.read_csv(f"resumen_{mes_actual}.csv")
    else:
        df_resumen = pd.DataFrame(columns=['Fecha', 'Total_Canasta', 'Variacion_Total', 'Porcentaje_Total', 'IPC_General'])
    
    if os.path.exists(f"divisiones_{mes_actual}.csv"):
        df_divisiones = pd.read_csv(f"divisiones_{mes_actual}.csv")
    else:
        df_divisiones = pd.DataFrame(columns=['Fecha', 'Division', 'Total', 'Variacion', 'Porcentaje', 'IPC'])
    
    if os.path.exists(f"productos_{mes_actual}.csv"):
        df_productos = pd.read_csv(f"productos_{mes_actual}.csv")
    else:
        df_productos = pd.DataFrame(columns=['Fecha', 'Producto', 'Division', 'Precio', 'Variacion', 'Porcentaje'])
    
    return df_resumen, df_divisiones, df_productos

def validar_division(division):
    """Valida si una división existe en las divisiones del IPC y sugiere la más cercana si no existe."""
    if division not in DIVISIONES_IPC:
        # Buscar la división más cercana
        sugerida = difflib.get_close_matches(division, DIVISIONES_IPC.keys(), n=1)
        if sugerida:
            print(f"Advertencia: División '{division}' no válida. ¿Quizás quisiste decir '{sugerida[0]}'?")
            return sugerida[0]
        else:
            # Si no hay sugerencia, asignar a una categoría general según el nombre
            if "pan" in division.lower() or "galletita" in division.lower():
                return "Panificados"
            elif "almacén" in division.lower() or "arroz" in division.lower() or "harina" in division.lower():
                return "Almacén"
            elif "fresco" in division.lower() or "fruta" in division.lower() or "verdura" in division.lower():
                return "Frescos"
            elif "bebida" in division.lower():
                return "Bebidas"
            else:
                print(f"Advertencia: División '{division}' no válida. Se asigna 'Alimentos y bebidas no alcohólicas' por defecto.")
                return "Alimentos y bebidas no alcohólicas"
    return division

def calcular_variacion_semanal(df_productos):
    """
    Calcula la variación promedio semanal de precios.
    
    Args:
        df_productos: DataFrame con los precios históricos
        
    Returns:
        DataFrame con la variación semanal promedio por producto
    """
    # Convertir la columna Fecha a datetime
    df_productos['Fecha'] = pd.to_datetime(df_productos['Fecha'])
    
    # Agregar columnas de año y semana
    df_productos['Año'] = df_productos['Fecha'].dt.isocalendar().year
    df_productos['Semana'] = df_productos['Fecha'].dt.isocalendar().week
    
    # Calcular el promedio semanal por producto
    promedios_semanales = df_productos.groupby(['Producto', 'Año', 'Semana'])['Precio'].mean().reset_index()
    
    # Ordenar por producto y semana
    promedios_semanales = promedios_semanales.sort_values(['Producto', 'Año', 'Semana'])
    
    # Calcular la variación semanal
    variaciones = []
    for producto in promedios_semanales['Producto'].unique():
        df_producto = promedios_semanales[promedios_semanales['Producto'] == producto]
        
        for i in range(1, len(df_producto)):
            precio_actual = df_producto.iloc[i]['Precio']
            precio_anterior = df_producto.iloc[i-1]['Precio']
            variacion = precio_actual - precio_anterior
            porcentaje = (variacion / precio_anterior) * 100
            
            variaciones.append({
                'Producto': producto,
                'Semana_Actual': df_producto.iloc[i]['Semana'],
                'Año_Actual': df_producto.iloc[i]['Año'],
                'Precio_Promedio_Actual': precio_actual,
                'Precio_Promedio_Anterior': precio_anterior,
                'Variacion': variacion,
                'Porcentaje': porcentaje
            })
    
    return pd.DataFrame(variaciones) 