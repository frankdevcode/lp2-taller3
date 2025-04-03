# Visualización de Datos Meteorológicos - Taller 3

![Python](https://img.shields.io/badge/python-3.12-blue)
![Flask](https://img.shields.io/badge/flask-2.3.3-green)
![Plotly](https://img.shields.io/badge/plotly-6.0.1-orange)

## Autor

- Francisco Perlaza

## Descripción del Proyecto

Este proyecto consiste en una aplicación web desarrollada con Flask que permite visualizar datos meteorológicos obtenidos de estaciones meteorológicas públicas a través de la API de ThingSpeak. La aplicación muestra gráficas interactivas de temperatura, humedad y presión atmosférica utilizando la biblioteca Plotly.

La aplicación permite:
- Visualizar datos históricos de diferentes estaciones meteorológicas
- Actualizar los datos en tiempo real
- Interactuar con las gráficas (zoom, pan, hover)
- Ver los datos de manera clara y organizada

## Tecnologías Utilizadas

- **Python 3.12**: Lenguaje de programación principal
- **Flask**: Framework web para el backend
- **Pandas**: Manipulación y análisis de datos
- **Plotly**: Generación de gráficas interactivas
- **Requests**: Comunicación con APIs externas
- **HTML/CSS**: Interfaz de usuario

## Instalación

1. Clonar el repositorio
```bash
git clone https://github.com/frankdevcode/lp2-taller3.git
```

2. Crear y activar entorno virtual
```bash
cd lp2-taller3
python -m venv venv
venv\Scripts\activate
```

3. Instalar librerías y dependencias
```bash
pip install -r requirements.txt
```
    
## Ejecución

1. Ejecutar la aplicación
```bash
python main.py
```

2. Abrir el navegador y acceder a la aplicación
```
http://127.0.0.1:5000
```

## Estructura del Proyecto

- **main.py**: Archivo principal que contiene la lógica de la aplicación
- **templates/**: Directorio con las plantillas HTML
  - **index.html**: Página principal que muestra las gráficas
- **static/**: Directorio donde se almacenan las gráficas generadas
- **requirements.txt**: Archivo con las dependencias del proyecto

## Funcionamiento

La aplicación se conecta a la API de ThingSpeak para obtener datos meteorológicos de estaciones públicas. Estos datos son procesados utilizando Pandas y visualizados con Plotly. Las gráficas generadas son interactivas y permiten al usuario explorar los datos de manera detallada.

El flujo de la aplicación es el siguiente:
1. Se descargan los datos de las estaciones meteorológicas
2. Se procesan y limpian los datos
3. Se generan las gráficas interactivas
4. Se muestran las gráficas en la interfaz web

## Mejoras Futuras

- Añadir más estaciones meteorológicas
- Implementar filtros por fecha
- Añadir más tipos de gráficas (barras, dispersión, etc.)
- Mejorar el diseño de la interfaz de usuario
- Implementar un sistema de alertas para condiciones meteorológicas extremas

## Referencias

- [ThingSpeak API Documentation](https://www.mathworks.com/help/thingspeak/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Plotly Python Documentation](https://plotly.com/python/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)
