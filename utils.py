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
            
            if precio_anterior != 0:
                porcentaje = (variacion / precio_anterior) * 100
            else:
                porcentaje = 0
            
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

def calcular_variacion_mensual(df_productos):
    """
    Calcula la variación mensual de precios para la canasta básica de alimentos.
    Compara el primer dato del mes con el último obtenido.
    
    Args:
        df_productos: DataFrame con los precios históricos
        
    Returns:
        DataFrame con la variación mensual por producto y división
    """
    # Convertir la columna Fecha a datetime
    df_productos['Fecha'] = pd.to_datetime(df_productos['Fecha'])
    
    # Agregar columnas de año y mes
    df_productos['Año'] = df_productos['Fecha'].dt.year
    df_productos['Mes'] = df_productos['Fecha'].dt.month
    
    # Filtrar solo las divisiones de alimentos básicos
    divisiones_alimentos = [
        "Alimentos y bebidas no alcohólicas",
        "Pan y cereales",
        "Panificados",
        "Almacén",
        "Frescos",
        "Bebidas"
    ]
    
    # Filtrar solo productos de alimentos básicos
    df_alimentos = df_productos[df_productos['Division'].isin(divisiones_alimentos)]
    
    # Obtener el primer y último dato del mes actual
    mes_actual = datetime.now().month
    año_actual = datetime.now().year
    
    # Filtrar datos del mes actual
    df_mes_actual = df_alimentos[
        (df_alimentos['Mes'] == mes_actual) & 
        (df_alimentos['Año'] == año_actual)
    ]
    
    if df_mes_actual.empty:
        return pd.DataFrame()  # Retornar DataFrame vacío si no hay datos del mes actual
    
    # Obtener el primer y último dato por producto
    variaciones = []
    for producto in df_mes_actual['Producto'].unique():
        df_producto = df_mes_actual[df_mes_actual['Producto'] == producto]
        
        # Ordenar por fecha
        df_producto = df_producto.sort_values('Fecha')
        
        if len(df_producto) >= 2:  # Necesitamos al menos dos datos
            primer_dato = df_producto.iloc[0]
            ultimo_dato = df_producto.iloc[-1]
            
            precio_actual = ultimo_dato['Precio']
            precio_anterior = primer_dato['Precio']
            variacion = precio_actual - precio_anterior
            
            if precio_anterior != 0:
                porcentaje = (variacion / precio_anterior) * 100
            else:
                porcentaje = 0
            
            variaciones.append({
                'Producto': producto,
                'Division': ultimo_dato['Division'],
                'Mes_Actual': mes_actual,
                'Año_Actual': año_actual,
                'Precio_Primer_Dia': precio_anterior,
                'Precio_Ultimo_Dia': precio_actual,
                'Variacion': variacion,
                'Porcentaje': porcentaje
            })
    
    return pd.DataFrame(variaciones)


def calcular_variacion_mensual_intermensual(df_productos):
    """Calcula la variación mensual comparando el promedio de precios del mes
    actual con el promedio del mes anterior para la canasta básica
    alimentaria."""

    df_productos['Fecha'] = pd.to_datetime(df_productos['Fecha'])

    df_productos['Año'] = df_productos['Fecha'].dt.year
    df_productos['Mes'] = df_productos['Fecha'].dt.month

    divisiones_alimentos = [
        "Alimentos y bebidas no alcohólicas",
        "Pan y cereales",
        "Panificados",
        "Almacén",
        "Frescos",
        "Bebidas",
    ]

    df_alimentos = df_productos[df_productos['Division'].isin(divisiones_alimentos)]

    fecha_actual = datetime.now()
    mes_actual = fecha_actual.month
    año_actual = fecha_actual.year

    fecha_mes_anterior = fecha_actual - pd.DateOffset(months=1)
    mes_anterior = fecha_mes_anterior.month
    año_anterior = fecha_mes_anterior.year

    df_mes_actual = df_alimentos[(df_alimentos['Mes'] == mes_actual) & (df_alimentos['Año'] == año_actual)]
    df_mes_anterior = df_alimentos[(df_alimentos['Mes'] == mes_anterior) & (df_alimentos['Año'] == año_anterior)]

    if df_mes_actual.empty or df_mes_anterior.empty:
        return pd.DataFrame()

    promedio_actual = df_mes_actual.groupby('Producto')['Precio'].mean()
    promedio_anterior = df_mes_anterior.groupby('Producto')['Precio'].mean()

    productos_comunes = promedio_actual.index.intersection(promedio_anterior.index)

    variaciones = []
    for producto in productos_comunes:
        precio_actual = promedio_actual[producto]
        precio_anterior = promedio_anterior[producto]
        variacion = precio_actual - precio_anterior
        porcentaje = (variacion / precio_anterior) * 100 if precio_anterior != 0 else 0
        division = df_mes_actual[df_mes_actual['Producto'] == producto].iloc[0]['Division']

        variaciones.append({
            'Producto': producto,
            'Division': division,
            'Mes_Actual': mes_actual,
            'Año_Actual': año_actual,
            'Precio_Promedio_Anterior': precio_anterior,
            'Precio_Promedio_Actual': precio_actual,
            'Variacion': variacion,
            'Porcentaje': porcentaje,
        })

    return pd.DataFrame(variaciones)
