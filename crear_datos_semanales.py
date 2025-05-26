import pandas as pd
from datetime import datetime, timedelta
import os

def crear_datos_semanales():
    """Crea archivos CSV con datos de prueba de varias semanas."""
    # Obtener fechas de las últimas 4 semanas
    fecha_actual = datetime.now()
    fechas = []
    for i in range(28):  # 4 semanas
        fecha = fecha_actual - timedelta(days=i)
        fechas.append(fecha.strftime('%Y-%m-%d %H:%M'))
    
    mes_actual = fecha_actual.strftime('%Y%m')
    
    # Crear DataFrame de productos con precios que varían semanalmente
    productos_prueba = []
    
    # Precios base
    precios_base = {
        "Galletita de Agua Cracker Dia 101 Gr": 470.00,
        "Arroz Largo Fino Molinos Ala 500 Gr.": 1040.00,
        "Leche Entera DIA Sachet 1 Lt.": 1390.00
    }
    
    # Variaciones semanales (porcentajes)
    variaciones = {
        "Galletita de Agua Cracker Dia 101 Gr": [0.05, 0.03, -0.02, 0.04],  # +5%, +3%, -2%, +4%
        "Arroz Largo Fino Molinos Ala 500 Gr.": [0.08, -0.03, 0.05, 0.02],  # +8%, -3%, +5%, +2%
        "Leche Entera DIA Sachet 1 Lt.": [0.04, 0.06, -0.01, 0.03]         # +4%, +6%, -1%, +3%
    }
    
    # Generar datos para cada producto
    for producto, precio_base in precios_base.items():
        precio_actual = precio_base
        for i, fecha in enumerate(fechas):
            # Calcular variación semanal
            semana = i // 7
            if semana < len(variaciones[producto]):
                variacion = variaciones[producto][semana]
                precio_actual = precio_base * (1 + variacion)
            
            productos_prueba.append({
                "Fecha": fecha,
                "Producto": producto,
                "Division": "Panificados" if producto == "Galletita" else "Almacén" if producto == "Arroz" else "Frescos",
                "Precio": precio_actual,
                "Variacion": None,
                "Porcentaje": None
            })
    
    # Crear DataFrame
    df_productos = pd.DataFrame(productos_prueba)
    
    # Guardar archivo CSV
    df_productos.to_csv(f"productos_{mes_actual}.csv", index=False)
    
    print("Archivo de prueba creado exitosamente:")
    print(f"- productos_{mes_actual}.csv")
    print("\nDatos generados para las últimas 4 semanas con variaciones semanales.")

if __name__ == "__main__":
    crear_datos_semanales() 