import json
from datetime import datetime
import os
from carrito import CarritoPersonal
from main import obtener_precio_dia

class ComparadorPrecios:
    def __init__(self, nombre_archivo="precios_diarios.txt"):
        self.nombre_archivo = nombre_archivo
        self.carrito = CarritoPersonal()
        self.precios_diarios = self.cargar_precios()

    def cargar_precios(self):
        precios = []
        if os.path.exists(self.nombre_archivo):
            with open(self.nombre_archivo, 'r', encoding='utf-8') as f:
                fecha_actual = None
                precios_dia = {}
                
                for linea in f:
                    if linea.startswith("FECHA:"):
                        if fecha_actual and precios_dia:
                            precios.append({
                                "fecha": fecha_actual,
                                "productos": precios_dia
                            })
                        fecha_actual = linea.strip().split(":")[1].strip()
                        precios_dia = {}
                    elif linea.strip() and "|" in linea:
                        nombre, precio = linea.strip().split("|")
                        precios_dia[nombre] = float(precio)
                
                if fecha_actual and precios_dia:
                    precios.append({
                        "fecha": fecha_actual,
                        "productos": precios_dia
                    })
        return precios

    def guardar_precios(self):
        with open(self.nombre_archivo, 'w', encoding='utf-8') as f:
            for dia in self.precios_diarios:
                f.write(f"FECHA: {dia['fecha']}\n")
                for nombre, precio in dia['productos'].items():
                    f.write(f"{nombre}|{precio}\n")
                f.write("\n")

    def actualizar_precios(self):
        fecha_actual = datetime.now().strftime("%Y-%m-%d")
        precios_actuales = {
            "fecha": fecha_actual,
            "productos": {}
        }

        for producto in self.carrito.productos:
            precio = obtener_precio_dia(producto["url"])
            if precio is not None:
                precios_actuales["productos"][producto["nombre"]] = precio

        self.precios_diarios.append(precios_actuales)
        self.guardar_precios()
        return precios_actuales

    def calcular_variacion(self):
        if len(self.precios_diarios) < 2:
            print("No hay suficientes datos para calcular la variación.")
            return

        ultimo = self.precios_diarios[-1]
        anterior = self.precios_diarios[-2]

        print("\n=== VARIACIÓN DE PRECIOS (IPC) ===")
        print(f"Fecha anterior: {anterior['fecha']}")
        print(f"Fecha actual: {ultimo['fecha']}\n")

        variaciones = []
        total_variacion = 0
        productos_analizados = 0

        for nombre, precio_actual in ultimo["productos"].items():
            if nombre in anterior["productos"]:
                precio_anterior = anterior["productos"][nombre]
                variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100
                variaciones.append(variacion)
                total_variacion += variacion
                productos_analizados += 1

                print(f"Producto: {nombre}")
                print(f"  Precio anterior: ${precio_anterior:.2f}")
                print(f"  Precio actual: ${precio_actual:.2f}")
                print(f"  Variación: {variacion:+.2f}%\n")

        if productos_analizados > 0:
            ipc = total_variacion / productos_analizados
            print("=== RESUMEN IPC ===")
            print(f"Variación promedio: {ipc:+.2f}%")
            print(f"Productos analizados: {productos_analizados}")

    def exportar_variacion(self):
        if len(self.precios_diarios) < 2:
            print("No hay suficientes datos para exportar la variación.")
            return

        nombre_archivo = f"variacion_precios_{datetime.now().strftime('%Y%m%d')}.txt"
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            ultimo = self.precios_diarios[-1]
            anterior = self.precios_diarios[-2]

            f.write("=== VARIACIÓN DE PRECIOS (IPC) ===\n")
            f.write(f"Fecha anterior: {anterior['fecha']}\n")
            f.write(f"Fecha actual: {ultimo['fecha']}\n\n")

            variaciones = []
            total_variacion = 0
            productos_analizados = 0

            for nombre, precio_actual in ultimo["productos"].items():
                if nombre in anterior["productos"]:
                    precio_anterior = anterior["productos"][nombre]
                    variacion = ((precio_actual - precio_anterior) / precio_anterior) * 100
                    variaciones.append(variacion)
                    total_variacion += variacion
                    productos_analizados += 1

                    f.write(f"Producto: {nombre}\n")
                    f.write(f"  Precio anterior: ${precio_anterior:.2f}\n")
                    f.write(f"  Precio actual: ${precio_actual:.2f}\n")
                    f.write(f"  Variación: {variacion:+.2f}%\n\n")

            if productos_analizados > 0:
                ipc = total_variacion / productos_analizados
                f.write("=== RESUMEN IPC ===\n")
                f.write(f"Variación promedio: {ipc:+.2f}%\n")
                f.write(f"Productos analizados: {productos_analizados}\n")

        print(f"Variación exportada a {nombre_archivo}")

# Ejemplo de uso
if __name__ == "__main__":
    comparador = ComparadorPrecios()
    
    while True:
        print("\n=== MENÚ DE COMPARACIÓN ===")
        print("1. Actualizar precios")
        print("2. Ver variación IPC")
        print("3. Exportar variación")
        print("4. Salir")
        
        opcion = input("\nSeleccione una opción (1-4): ")
        
        if opcion == "1":
            print("Actualizando precios...")
            comparador.actualizar_precios()
            print("¡Precios actualizados!")
        
        elif opcion == "2":
            comparador.calcular_variacion()
        
        elif opcion == "3":
            comparador.exportar_variacion()
        
        elif opcion == "4":
            print("¡Hasta luego!")
            break
        
        else:
            print("Opción no válida. Por favor, seleccione una opción del 1 al 4.") 