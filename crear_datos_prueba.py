import pandas as pd
from datetime import datetime, timedelta
import os

def crear_datos_prueba():
    """Crea archivos CSV con datos de prueba de ayer con precios 10% más altos."""
    # Obtener fecha de ayer
    fecha_ayer = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M')
    mes_actual = datetime.now().strftime('%Y%m')
    
    # Crear DataFrame de productos con precios 10% más altos
    productos_prueba = [
        {
            "Fecha": fecha_ayer,
            "Producto": "Galletita de Agua Cracker Dia 101 Gr",
            "Division": "Panificados",
            "Precio": 517.00,  # 470 * 1.1
            "Variacion": None,
            "Porcentaje": None
        },
        {
            "Fecha": fecha_ayer,
            "Producto": "Arroz Largo Fino Molinos Ala 500 Gr.",
            "Division": "Almacén",
            "Precio": 1144.00,  # 1040 * 1.1
            "Variacion": None,
            "Porcentaje": None
        },
        {
            "Fecha": fecha_ayer,
            "Producto": "Leche Entera DIA Sachet 1 Lt.",
            "Division": "Frescos",
            "Precio": 1529.00,  # 1390 * 1.1
            "Variacion": None,
            "Porcentaje": None
        }
    ]
    
    # Crear DataFrame de divisiones
    divisiones_prueba = [
        {
            "Fecha": fecha_ayer,
            "Division": "Panificados",
            "Total": 2585.00,  # 517 * 5
            "Variacion": None,
            "Porcentaje": None,
            "IPC": None
        },
        {
            "Fecha": fecha_ayer,
            "Division": "Almacén",
            "Total": 3432.00,  # 1144 * 3
            "Variacion": None,
            "Porcentaje": None,
            "IPC": None
        },
        {
            "Fecha": fecha_ayer,
            "Division": "Frescos",
            "Total": 15290.00,  # 1529 * 10
            "Variacion": None,
            "Porcentaje": None,
            "IPC": None
        }
    ]
    
    # Crear DataFrame de resumen
    resumen_prueba = [
        {
            "Fecha": fecha_ayer,
            "Total_Canasta": 21307.00,  # Suma de todos los totales
            "Variacion_Total": None,
            "Porcentaje_Total": None,
            "IPC_General": None
        }
    ]
    
    # Crear los DataFrames
    df_productos = pd.DataFrame(productos_prueba)
    df_divisiones = pd.DataFrame(divisiones_prueba)
    df_resumen = pd.DataFrame(resumen_prueba)
    
    # Guardar los archivos CSV
    df_productos.to_csv(f"productos_{mes_actual}.csv", index=False)
    df_divisiones.to_csv(f"divisiones_{mes_actual}.csv", index=False)
    df_resumen.to_csv(f"resumen_{mes_actual}.csv", index=False)
    
    print("Archivos de prueba creados exitosamente:")
    print(f"- productos_{mes_actual}.csv")
    print(f"- divisiones_{mes_actual}.csv")
    print(f"- resumen_{mes_actual}.csv")
    print("\nLos precios de ayer son 10% más altos que los actuales.")

if __name__ == "__main__":
    crear_datos_prueba() 