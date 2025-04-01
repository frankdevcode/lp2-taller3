from flask import Flask, render_template
import pandas as pd

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
  df.drop(['entry_id', 'field5', 'field6'])

@app.route('/')
def index():
  return render_template('index.html')
  # Lee el CSV desde la URL

# Programa Principal
if __name__ == '__main__':   
  # Ejecuta la app
  app.run(host='0.0.0.0', debug=True)
