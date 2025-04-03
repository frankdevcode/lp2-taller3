import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def calcular_tendencia(df, columna, ventana=24):
    """
    Calcula la tendencia de una variable meteorológica basada en datos históricos.
    
    Args:
        df: DataFrame con los datos
        columna: Nombre de la columna a analizar
        ventana: Tamaño de la ventana para calcular la tendencia (en horas)
        
    Returns:
        tendencia: 'ascendente', 'descendente' o 'estable'
        cambio: Porcentaje de cambio
    """
    if df.empty or len(df) < ventana:
        return 'desconocida', 0
    
    # Obtener los datos más recientes
    df_reciente = df.tail(ventana)
    
    # Calcular la tendencia usando regresión lineal simple
    y = df_reciente[columna].values
    x = np.arange(len(y))
    
    # Calcular la pendiente (m) en y = mx + b
    if len(x) > 1 and len(y) > 1:
        m = np.polyfit(x, y, 1)[0]
        
        # Calcular el porcentaje de cambio
        if len(y) > 0 and y[0] != 0:
            cambio_porcentaje = (m * len(y)) / y[0] * 100
        else:
            cambio_porcentaje = 0
            
        # Determinar la tendencia basada en la pendiente
        if m > 0.01:
            return 'ascendente', cambio_porcentaje
        elif m < -0.01:
            return 'descendente', cambio_porcentaje
        else:
            return 'estable', cambio_porcentaje
    
    return 'desconocida', 0

def predecir_proximo_valor(df, columna, horas=24):
    """
    Predice el valor de una variable meteorológica para las próximas horas.
    
    Args:
        df: DataFrame con los datos
        columna: Nombre de la columna a predecir
        horas: Número de horas a predecir
        
    Returns:
        valor_predicho: Valor predicho para las próximas horas
    """
    if df.empty or len(df) < 24:
        return None
    
    # Obtener los datos más recientes
    df_reciente = df.tail(48)  # Usar los últimos 2 días para la predicción
    
    # Calcular la tendencia usando regresión lineal simple
    y = df_reciente[columna].values
    x = np.arange(len(y))
    
    if len(x) > 1 and len(y) > 1:
        # Calcular los coeficientes (pendiente e intercepto)
        coef = np.polyfit(x, y, 1)
        
        # Predecir el valor para las próximas horas
        valor_predicho = coef[0] * (len(y) + horas) + coef[1]
        
        return round(valor_predicho, 2)
    
    return None

def generar_alerta(df, columna):
    """
    Genera alertas basadas en valores extremos o cambios rápidos.
    
    Args:
        df: DataFrame con los datos
        columna: Nombre de la columna a analizar
        
    Returns:
        alerta: Diccionario con tipo de alerta y mensaje
    """
    if df.empty:
        return None
    
    # Definir umbrales para cada tipo de variable
    umbrales = {
        'temperatura': {'alto': 35, 'bajo': 0, 'cambio_rapido': 10},
        'humedad': {'alto': 90, 'bajo': 20, 'cambio_rapido': 30},
        'presion': {'alto': 1040, 'bajo': 990, 'cambio_rapido': 15}
    }
    
    # Determinar qué tipo de variable es basado en el nombre de la columna
    tipo_variable = None
    for key in umbrales.keys():
        if key in columna.lower():
            tipo_variable = key
            break
    
    if tipo_variable is None:
        return None
    
    # Obtener el valor más reciente
    valor_reciente = df[columna].iloc[-1] if len(df) > 0 else None
    
    if valor_reciente is None:
        return None
    
    # Calcular el cambio en las últimas 6 horas
    if len(df) >= 6:
        valor_anterior = df[columna].iloc[-6]
        cambio = abs(valor_reciente - valor_anterior)
    else:
        cambio = 0
    
    # Generar alertas basadas en los umbrales
    if valor_reciente > umbrales[tipo_variable]['alto']:
        return {
            'tipo': 'alto',
            'nivel': 'advertencia',
            'mensaje': f"{tipo_variable.capitalize()} alta: {valor_reciente}",
            'color': 'red'
        }
    elif valor_reciente < umbrales[tipo_variable]['bajo']:
        return {
            'tipo': 'bajo',
            'nivel': 'advertencia',
            'mensaje': f"{tipo_variable.capitalize()} baja: {valor_reciente}",
            'color': 'blue'
        }
    elif cambio > umbrales[tipo_variable]['cambio_rapido']:
        return {
            'tipo': 'cambio_rapido',
            'nivel': 'precaución',
            'mensaje': f"Cambio rápido en {tipo_variable}: {cambio} en 6 horas",
            'color': 'orange'
        }
    
    return None

def analizar_datos_meteorologicos(df, columna):
    """
    Analiza los datos meteorológicos para generar predicciones y alertas.
    
    Args:
        df: DataFrame con los datos
        columna: Nombre de la columna a analizar
        
    Returns:
        resultado: Diccionario con tendencia, predicción y alertas
    """
    resultado = {}
    
    # Calcular tendencia
    tendencia, cambio = calcular_tendencia(df, columna)
    resultado['tendencia'] = tendencia
    resultado['cambio_porcentaje'] = round(cambio, 2)
    
    # Predecir próximo valor
    prediccion_24h = predecir_proximo_valor(df, columna, 24)
    resultado['prediccion_24h'] = prediccion_24h
    
    # Generar alertas
    alerta = generar_alerta(df, columna)
    resultado['alerta'] = alerta
    
    return resultado
