import pandas as pd
from datetime import datetime

def generar_resumen_pro():
    # Obtener el nombre del archivo del mes actual
    nombre_archivo = f"resumen_{datetime.now().strftime('%Y%m')}.csv"
    
    # Leer el archivo CSV
    df = pd.read_csv(nombre_archivo)
    
    # Convertir la columna Fecha a datetime
    df['Fecha'] = pd.to_datetime(df['Fecha'])
    
    # Obtener el primer día del mes
    primer_dia = df.iloc[0]
    
    # Calcular la variación porcentual desde el primer día
    df['Variacion_Desde_Primer_Dia'] = ((df['Total_Canasta'] - primer_dia['Total_Canasta']) / primer_dia['Total_Canasta']) * 100
    
    # Generar el resumen Pro
    resumen_pro = []
    resumen_pro.append("=== RESUMEN PRO DE LA CANASTA ===")
    resumen_pro.append(f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    resumen_pro.append("\nResumen por día:")
    
    for _, row in df.iterrows():
        resumen_pro.append(f"\nFecha: {row['Fecha'].strftime('%Y-%m-%d %H:%M')}")
        resumen_pro.append(f"Total Canasta: ${row['Total_Canasta']:,.2f}")
        
        if pd.notna(row['Variacion_Total']):
            signo = "+" if row['Variacion_Total'] >= 0 else ""
            resumen_pro.append(f"Variación diaria: {signo}${row['Variacion_Total']:,.2f} ({signo}{row['Porcentaje_Total']:.2f}%)")
        
        signo_pro = "+" if row['Variacion_Desde_Primer_Dia'] >= 0 else ""
        resumen_pro.append(f"Variación desde primer día: {signo_pro}{row['Variacion_Desde_Primer_Dia']:.2f}%")
        
        if pd.notna(row['IPC_General']):
            signo_ipc = "+" if row['IPC_General'] >= 0 else ""
            resumen_pro.append(f"IPC General: {signo_ipc}{row['IPC_General']:.2f}%")
    
    # Guardar el resumen en un archivo
    nombre_archivo_txt = f"resumen_pro_{datetime.now().strftime('%Y%m')}.txt"
    nombre_archivo_csv = f"resumen_pro_{datetime.now().strftime('%Y%m')}.csv"
    
    with open(nombre_archivo_txt, 'w', encoding='utf-8') as f:
        f.write('\n'.join(resumen_pro))
    
    # Guardar también en CSV
    df.to_csv(nombre_archivo_csv, index=False)
    
    print("Resumen Pro generado exitosamente!")
    print("Archivos creados:")
    print(f"- {nombre_archivo_txt}")
    print(f"- {nombre_archivo_csv}")

if __name__ == "__main__":
    generar_resumen_pro() 