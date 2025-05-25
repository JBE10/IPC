# Seguimiento de Precios DIA

Este proyecto permite realizar un seguimiento de los precios de productos específicos del supermercado DIA en Argentina, utilizando su API pública.

## Características

- Extracción de precios en tiempo real de productos DIA
- Seguimiento de precios a lo largo del tiempo
- Exportación de datos en formato CSV para análisis
- Cálculo automático del total de la canasta

## Requisitos

- Python 3.9 o superior
- pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/JBE10/IPC.git
cd IPC
```

2. Crear y activar un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

## Uso

1. Configurar los productos en `mi_carrito.txt`:
```
URL_DEL_PRODUCTO;NOMBRE_DEL_PRODUCTO
```

2. Ejecutar el script:
```bash
python main.py
```

El script generará:
- Un archivo CSV (`seguimiento_precios.csv`) con el historial de precios
- Un archivo de texto con el resumen del día

## Estructura del Proyecto

- `main.py`: Script principal para obtener y registrar precios
- `mi_carrito.txt`: Lista de productos a monitorear
- `seguimiento_precios.csv`: Historial de precios
- `requirements.txt`: Dependencias del proyecto

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles. 