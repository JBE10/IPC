import json
from datetime import datetime
import os

class CarritoPersonal:
    def __init__(self, nombre_archivo="mi_carrito.txt"):
        self.nombre_archivo = nombre_archivo
        self.productos = self.cargar_carrito()

    def cargar_carrito(self):
        productos = []
        if os.path.exists(self.nombre_archivo):
            with open(self.nombre_archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    if linea.strip():
                        url, nombre = linea.strip().split(';')
                        productos.append({
                            "nombre": nombre.strip(),
                            "url": url.strip(),
                            "cantidad": 1,  # Cantidad por defecto
                            "fecha_agregado": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        })
        return productos

    def guardar_carrito(self):
        with open(self.nombre_archivo, 'w', encoding='utf-8') as f:
            for producto in self.productos:
                f.write(f"{producto['nombre']}|{producto['url']}|{producto['cantidad']}\n")

    def agregar_producto(self, nombre, url, cantidad=1):
        producto = {
            "nombre": nombre,
            "url": url,
            "cantidad": cantidad,
            "fecha_agregado": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.productos.append(producto)
        self.guardar_carrito()
        print(f"Producto '{nombre}' agregado al carrito.")

    def eliminar_producto(self, nombre):
        self.productos = [p for p in self.productos if p["nombre"] != nombre]
        self.guardar_carrito()
        print(f"Producto '{nombre}' eliminado del carrito.")

    def modificar_cantidad(self, nombre, nueva_cantidad):
        for producto in self.productos:
            if producto["nombre"] == nombre:
                producto["cantidad"] = nueva_cantidad
                self.guardar_carrito()
                print(f"Cantidad de '{nombre}' actualizada a {nueva_cantidad}.")
                return
        print(f"Producto '{nombre}' no encontrado en el carrito.")

    def mostrar_carrito(self):
        if not self.productos:
            print("El carrito está vacío.")
            return

        print("\n=== MI CARRITO DE COMPRAS ===")
        print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
        
        for producto in self.productos:
            print(f"- {producto['nombre']}")
            print(f"  URL: {producto['url']}\n")

# Ejemplo de uso
if __name__ == "__main__":
    carrito = CarritoPersonal()
    carrito.mostrar_carrito()
    
    while True:
        print("\n=== MENÚ DEL CARRITO ===")
        print("1. Ver carrito")
        print("2. Agregar producto")
        print("3. Eliminar producto")
        print("4. Modificar cantidad")
        print("5. Salir")
        
        opcion = input("\nSeleccione una opción (1-5): ")
        
        if opcion == "1":
            carrito.mostrar_carrito()
        
        elif opcion == "2":
            nombre = input("Nombre del producto: ")
            url = input("URL del producto en DIA: ")
            cantidad = int(input("Cantidad: "))
            carrito.agregar_producto(nombre, url, cantidad)
        
        elif opcion == "3":
            nombre = input("Nombre del producto a eliminar: ")
            carrito.eliminar_producto(nombre)
        
        elif opcion == "4":
            nombre = input("Nombre del producto: ")
            cantidad = int(input("Nueva cantidad: "))
            carrito.modificar_cantidad(nombre, cantidad)
        
        elif opcion == "5":
            print("¡Hasta luego!")
            break
        
        else:
            print("Opción no válida. Por favor, seleccione una opción del 1 al 5.") 