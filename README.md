# IPC Personal - Seguimiento de Precios

Este proyecto permite realizar un seguimiento personalizado de precios de productos de supermercados, calculando variaciones diarias y generando un IPC (Índice de Precios al Consumidor) personalizado.

## Características

- Gestión de carrito personal de productos
- Seguimiento diario de precios
- Cálculo de variaciones porcentuales
- Generación de IPC personalizado
- Exportación de reportes en formato TXT

## Requisitos

- Python 3.6 o superior
- Módulos requeridos:
  - requests
  - beautifulsoup4
  - datetime

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/JBE10/IPC.git
cd IPC
```

2. Instalar dependencias:
```bash
pip install -r requirements.txt
```

## Uso

### Gestión del Carrito

```bash
python carrito.py
```

Opciones disponibles:
- Ver carrito
- Agregar producto
- Eliminar producto
- Modificar cantidad

### Seguimiento de Precios

```bash
python comparador.py
```

Opciones disponibles:
- Actualizar precios
- Ver variación IPC
- Exportar variación

## Estructura de Archivos

- `carrito.py`: Gestión del carrito personal
- `comparador.py`: Seguimiento y análisis de precios
- `main.py`: Funciones principales de scraping
- `mi_carrito.txt`: Carrito personal (se crea automáticamente)
- `precios_diarios.txt`: Historial de precios (se crea automáticamente)

## Contribuir

1. Fork el proyecto
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles. 