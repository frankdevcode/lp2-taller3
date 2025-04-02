from flask import Flask, render_template
import pandas as pd
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use('Agg') # Para evitar el error de X11 en el servidor

# Buscar en ThingSpeak estaciones meteorológicas:
# https://thingspeak.mathworks.com/channels/public
# Ejemplos:
# https://thingspeak.mathworks.com/channels/870845
# https://thingspeak.mathworks.com/channels/1293177
# https://thingspeak.mathworks.com/channels/12397

URLs = [
  'https://api.thingspeak.com/channels/159150/feeds.csv?results=800',
  'https://api.thingspeak.com/channels/196384/feeds.csv?results=800',
  'https://api.thingspeak.com/channels/178434/feeds.csv?results=800',
]

app = Flask(__name__)

def descargar(url):
  # Descarga el CSV en un DataFrame, desde la URL
  df = pd.read_csv(url)
  #convertir la cadena en una feccha real
  df['created_at'] = pd.to_datetime(df['created_at'])
  # Borar las columnas que no se van a usar
  if 'field6' in df.columns:
    df.drop(['entry_id', 'field5', 'field6'], axis=1, inplace=True)
  else:
    df.drop(['entry_id', 'field5', 'field7'], axis=1, inplace=True)
  # Renombrar las columnas
  df.columns = ['fecha', 'tem_exterior', 'presion_atm', 'humedad']
  return df

def graficar(df):
  lista = []
  for colmna in df.columns[1:]:
    # Crear la figura
    fig = plt.figure(figsize=(8, 5))
    # Hacer la gráfica
    plt.plot(df['fecha'], df[colmna], label=colmna)
    # Poner los títulos
    plt.title(f"Histórico de {colmna}")
    # Grabar la imagen
    plt.savefig(f"static/{colmna}.png")
    lista.append(f"{colmna}.png")
    plt.close(fig)
  return lista

@app.route('/')
def index():
  # Descarga los datos y genera las gráficas
  for url in URLs:
    nombres = []
    df = descargar(url)
    nombres.extend(graficar(df))

  return render_template('index.html', nombres=nombres)
  # Lee el CSV desde la URL

# Programa Principal
if __name__ == '__main__':   
  app.run(host='0.0.0.0', debug=True)
