from flask import Flask, render_template, redirect, url_for, jsonify
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import requests
import numpy as np
from datetime import datetime, timedelta
from prediccion import analizar_datos_meteorologicos

# Buscar en ThingSpeak estaciones meteorológicas:
# https://thingspeak.mathworks.com/channels/public
# Ejemplos actualizados de canales públicos de ThingSpeak:
# https://thingspeak.com/channels/38629
# https://thingspeak.com/channels/12397
# https://thingspeak.com/channels/1848295

URLs = [
  'https://api.thingspeak.com/channels/38629/feeds.json?results=800',
  'https://api.thingspeak.com/channels/12397/feeds.json?results=800',
  'https://api.thingspeak.com/channels/1848295/feeds.json?results=800',
]

graficas_json = []
datos_estaciones = []  # Almacenar los DataFrames de cada estación
predicciones = []  # Almacenar las predicciones para cada estación

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
        if isinstance(obj, pd.Timestamp):
            return obj.isoformat()
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
  predicciones_estacion = []
  
  # Si el DataFrame está vacío, no generar gráficas
  if df.empty:
    print(f"DataFrame vacío para la estación #{i}, no se generarán gráficas")
    return graficas, predicciones_estacion
  
  # Obtener las columnas de datos (todas excepto 'fecha')
  data_columns = [col for col in df.columns if col != 'fecha']
  
  for columna in data_columns:
    try:
      # Convertir la columna a tipo numérico si no lo es
      if not pd.api.types.is_numeric_dtype(df[columna]):
        df[columna] = pd.to_numeric(df[columna], errors='coerce')
        df = df.dropna(subset=[columna])  # Eliminar filas con valores no numéricos
      
      # Analizar datos para predicciones y alertas
      analisis = analizar_datos_meteorologicos(df, columna)
      predicciones_estacion.append({
        'estacion': i,
        'variable': columna,
        'analisis': analisis
      })
      
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
      
      # Añadir predicción si existe
      if analisis['prediccion_24h'] is not None:
        ultima_fecha = df['fecha'].iloc[-1]
        fecha_prediccion = ultima_fecha + timedelta(hours=24)
        
        # Añadir punto de predicción
        fig.add_trace(
          go.Scatter(
            x=[fecha_prediccion],
            y=[analisis['prediccion_24h']],
            mode='markers',
            marker=dict(size=10, color='red'),
            name='Predicción 24h',
            hovertemplate=f"Predicción para %{{x}}: %{{y:.2f}}<br>Tendencia: {analisis['tendencia']} ({analisis['cambio_porcentaje']}%)"
          )
        )
        
        # Añadir línea de tendencia
        fig.add_trace(
          go.Scatter(
            x=[df['fecha'].iloc[-1], fecha_prediccion],
            y=[df[columna].iloc[-1], analisis['prediccion_24h']],
            mode='lines',
            line=dict(dash='dash', color='red'),
            name='Tendencia',
            hoverinfo='skip'
          )
        )
      
      # Añadir alerta si existe
      if analisis['alerta'] is not None:
        fig.add_annotation(
          x=df['fecha'].iloc[-1],
          y=df[columna].iloc[-1],
          text=str(analisis['alerta']['mensaje']),  # Asegurar que sea string
          showarrow=True,
          arrowhead=1,
          arrowcolor=analisis['alerta']['color'],
          arrowsize=1,
          arrowwidth=2,
          bgcolor=analisis['alerta']['color'],
          bordercolor="#c7c7c7",
          borderwidth=2,
          borderpad=4,
          font=dict(color="white"),
          opacity=0.8
        )
      
      # Guardar como HTML
      nombre_archivo = f"g{i}_{columna}.html"
      fig.write_html(f"static/{nombre_archivo}")
      
      # Convertir la figura a un diccionario y luego a JSON usando el encoder personalizado
      fig_dict = fig.to_dict()
      grafica_json = json.dumps(fig_dict, cls=NumpyEncoder)
      
      graficas.append({
        'titulo': f"Histórico de {columna} - Estación #{i}",
        'json': grafica_json
      })
      
    except Exception as e:
      print(f"Error al generar gráfica para {columna}: {e}")
  
  return graficas, predicciones_estacion

def actualizar():
  # Descarga los datos y genera las gráficas
  graficas = []
  predicciones_todas = []
  datos_todas = []
  
  for i, url in enumerate(URLs):
    try:
      print(f"Descargando datos de la URL: {url}")
      df = descargar(url)
      if not df.empty:
        print(f"Datos descargados correctamente. Filas: {len(df)}, Columnas: {df.columns.tolist()}")
        datos_todas.append(df)
        graficas_estacion, predicciones_estacion = generar_graficas(i, df)
        graficas.extend(graficas_estacion)
        predicciones_todas.extend(predicciones_estacion)
      else:
        print(f"No se pudieron obtener datos de la URL: {url}")
        datos_todas.append(pd.DataFrame())
    except Exception as e:
      print(f"Error al procesar URL {url}: {e}")
      datos_todas.append(pd.DataFrame())
  
  return graficas, predicciones_todas, datos_todas

@app.route('/')
def index():
  global graficas_json, predicciones
  # Si no hay gráficas, actualizar los datos
  if not graficas_json:
    graficas_json, predicciones, datos_estaciones = actualizar()
  
  # Organizar las predicciones por estación
  predicciones_por_estacion = {}
  for pred in predicciones:
    estacion = pred['estacion']
    if estacion not in predicciones_por_estacion:
      predicciones_por_estacion[estacion] = []
    predicciones_por_estacion[estacion].append(pred)
  
  return render_template('index.html', 
                         graficas=graficas_json, 
                         predicciones=predicciones_por_estacion)

@app.route('/actualizar')
def actualizar_datos():
  # Actualiza los datos y redirigir a la página principal
  global graficas_json, predicciones, datos_estaciones
  graficas_json, predicciones, datos_estaciones = actualizar()
  return redirect(url_for('index'))

@app.route('/predicciones')
def ver_predicciones():
  # Mostrar la página de predicciones detalladas
  predicciones_por_estacion = {}
  
  # Organizar las predicciones por estación
  for pred in predicciones:
    estacion = pred['estacion']
    if estacion not in predicciones_por_estacion:
      predicciones_por_estacion[estacion] = []
    predicciones_por_estacion[estacion].append(pred)
  
  return render_template('predicciones.html', predicciones=predicciones_por_estacion)

@app.route('/api/predicciones')
def api_predicciones():
  # Endpoint API para obtener las predicciones en formato JSON
  return jsonify(predicciones)

# Programa Principal
if __name__ == '__main__':   
  # Asegurarse de que la carpeta static existe
  os.makedirs('static', exist_ok=True)
  # Actualizar los datos antes de iniciar el servidor
  graficas_json, predicciones, datos_estaciones = actualizar()
  print(f"Gráficas generadas: {len(graficas_json)}")
  print(f"Predicciones generadas: {len(predicciones)}")
  app.run(host='0.0.0.0', debug=True)
