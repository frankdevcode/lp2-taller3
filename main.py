from flask import Flask, render_template, redirect, url_for
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import requests
import numpy as np
from datetime import datetime, timedelta

# Buscar en ThingSpeak estaciones meteorológicas:
# https://thingspeak.mathworks.com/channels/public
# Ejemplos actualizados de canales públicos de ThingSpeak:
# https://thingspeak.com/channels/38629
# https://thingspeak.com/channels/1722286
# https://thingspeak.com/channels/2113417

URLs = [
  'https://api.thingspeak.com/channels/38629/feeds.json?results=800',
  'https://api.thingspeak.com/channels/1722286/feeds.json?results=800',
  'https://api.thingspeak.com/channels/2113417/feeds.json?results=800',
]

graficas_json = []

app = Flask(__name__)

# Clase personalizada para manejar la serialización de objetos NumPy
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)

def descargar(url):
  # Descarga el CSV en un DataFrame, desde la URL
  try:
    # Usar requests para obtener los datos
    response = requests.get(url)
    response.raise_for_status()  # Lanzar excepción si hay error HTTP
    
    # Convertir JSON a DataFrame
    data = response.json()
    feeds = data.get('feeds', [])
    
    if not feeds:
      print(f"No se encontraron datos en la URL: {url}")
      return pd.DataFrame()
      
    # Crear DataFrame
    df = pd.DataFrame(feeds)
    
    # Convertir la cadena en una fecha real
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # Seleccionar solo las columnas que necesitamos
    # Primero identificar qué columnas de field están disponibles
    field_columns = [col for col in df.columns if col.startswith('field')]
    
    # Seleccionar las primeras 3 columnas field si están disponibles
    selected_fields = field_columns[:3] if len(field_columns) >= 3 else field_columns
    
    if not selected_fields:
      print(f"No se encontraron campos de datos en la URL: {url}")
      return pd.DataFrame()
    
    # Seleccionar solo las columnas que necesitamos
    df = df[['created_at'] + selected_fields]
    
    # Renombrar las columnas según los campos disponibles
    new_names = {
      'created_at': 'fecha'
    }
    
    # Asignar nombres a las columnas de datos
    data_names = ['temperatura', 'humedad', 'presion']
    for i, field in enumerate(selected_fields):
      if i < len(data_names):
        new_names[field] = data_names[i]
    
    # Renombrar las columnas
    df = df.rename(columns=new_names)
    
    # Eliminar filas con valores nulos
    df = df.dropna()
    
    return df
    
  except requests.exceptions.RequestException as e:
    print(f"Error al descargar datos: {e}")
    # Crear un DataFrame vacío
    return pd.DataFrame()
  except Exception as e:
    print(f"Error inesperado al procesar datos: {e}")
    return pd.DataFrame()

def generar_graficas(i, df):
  # Asegurarse de que la carpeta static existe
  os.makedirs('static', exist_ok=True)
  
  graficas = []
  
  # Si el DataFrame está vacío, no generar gráficas
  if df.empty:
    print(f"DataFrame vacío para la estación #{i}, no se generarán gráficas")
    return graficas
  
  # Obtener las columnas de datos (todas excepto 'fecha')
  data_columns = [col for col in df.columns if col != 'fecha']
  
  for columna in data_columns:
    try:
      # Crear la figura con Plotly
      fig = px.line(df, x='fecha', y=columna, 
                    title=f"Histórico de {columna} - Estación #{i}",
                    labels={'fecha': 'Fecha', columna: columna})
      
      # Mejorar el diseño
      fig.update_layout(
        xaxis_title="Fecha",
        yaxis_title=columna,
        legend_title="Leyenda",
        font=dict(family="Arial, sans-serif", size=12),
        margin=dict(l=50, r=50, t=80, b=50),
      )
      
      # Guardar como HTML
      nombre_archivo = f"g{i}_{columna}.html"
      fig.write_html(f"static/{nombre_archivo}")
      
      # Convertir la figura a un diccionario y luego a JSON usando el encoder personalizado
      fig_dict = fig.to_dict()
      grafica_json = json.dumps(fig_dict, cls=NumpyEncoder)
      
      graficas.append({
        'nombre': nombre_archivo,
        'titulo': f"Histórico de {columna} - Estación #{i}",
        'json': grafica_json
      })
      
      print(f"Gráfica generada: {nombre_archivo}")
      
    except Exception as e:
      print(f"Error al generar gráfica para {columna}: {e}")
    
  return graficas

def actualizar():
  # Descarga los datos y genera las gráficas
  graficas = []
  for i, url in enumerate(URLs):
    try:
      print(f"Descargando datos de la URL: {url}")
      df = descargar(url)
      if not df.empty:
        print(f"Datos descargados correctamente. Filas: {len(df)}, Columnas: {df.columns.tolist()}")
        graficas.extend(generar_graficas(i, df))
      else:
        print(f"No se pudieron obtener datos de la URL: {url}")
    except Exception as e:
      print(f"Error al procesar URL {url}: {e}")
  return graficas

@app.route('/')
def index():
  global graficas_json
  # Si no hay gráficas, actualizar los datos
  if not graficas_json:
    graficas_json = actualizar()
  return render_template('index.html', graficas=graficas_json)

@app.route('/actualizar')
def actualizar_datos():
  # Actualiza los datos y las gráficas
  global graficas_json
  graficas_json = actualizar()
  return redirect(url_for('index'))
  
# Programa Principal
if __name__ == '__main__':   
  # Asegurarse de que la carpeta static existe
  os.makedirs('static', exist_ok=True)
  # Actualizar los datos antes de iniciar el servidor
  graficas_json = actualizar()
  print(f"Gráficas generadas: {len(graficas_json)}")
  app.run(host='0.0.0.0', debug=True)
