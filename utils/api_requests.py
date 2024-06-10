import requests
import pandas as pd
from utils.time_tools import convert_to_hour_minutes

def get_cities(search_string):
    url = 'https://geocoding-api.open-meteo.com/v1/search'
    params = { 'name': search_string, 'count': 5, 'language': 'pt', format: 'json' }
    response = requests.get(url, params=params)
    data = response.json()['results']
    
    cidades = []
    coordenadas = []
    for city in range(len(data)):
        try:
            name = data[city]['name']
            region = data[city]['admin1']
            country = data[city]['country']
            cidade = f"{name}, {region}, {country}"
        except KeyError:
            name = data[city]['name']
            country = data[city]['country']
            cidade = f"{name}, {country}"
        lat = data[city]['latitude']
        lon = data[city]['longitude']
        
        cidades.append(cidade)
        coordenadas.append((lat, lon))
    
    result = list(zip(cidades, coordenadas))
    return result

def get_weather(lat, lon, start_date, end_date):
    url = 'https://archive-api.open-meteo.com/v1/era5'
    info = ['temperature_2m_max', 'temperature_2m_min',
            'precipitation_hours', 'rain_sum', 'snowfall_sum', 'wind_speed_10m_max',
            'daylight_duration', 'sunrise', 'sunset']
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': start_date,
        'end_date': end_date,
        'timezone': 'auto',
        'daily': info }
    response = requests.get(url, params=params)
    daily_data =  response.json()['daily']
    daily_data['Data'] = daily_data.pop('time')
    
    daily_data['Máxima'] = daily_data.pop('temperature_2m_max')
    daily_data['Mínima'] = daily_data.pop('temperature_2m_min')
    
    daily_data['Precipitação_h'] = daily_data.pop('precipitation_hours')
    daily_data['Chuva_mm'] = daily_data.pop('rain_sum')
    daily_data['Neve_cm'] = daily_data.pop('snowfall_sum')
    daily_data['Vento_max'] = daily_data.pop('wind_speed_10m_max')
    
    daily_data['Horas_sol'] = [round(d/3600, 0) for d in daily_data.pop('daylight_duration')]
    daily_data['Nascer_do_sol'] = [convert_to_hour_minutes(x) for x in daily_data.pop('sunrise')]
    daily_data['Por_do_sol'] = [convert_to_hour_minutes(x) for x in daily_data.pop('sunset')]
    
    df = pd.DataFrame(daily_data)
    df['Ano'] = pd.to_datetime(df['Data']).dt.year
    df['Mes'] = pd.to_datetime(df['Data']).dt.month    
    df['Data'] = pd.to_datetime(df['Data']).dt.date
    
    return df

def get_forecast(lat, lon, start_date, end_date):
    url = 'https://ensemble-api.open-meteo.com/v1/ensemble'
    info = ['temperature_2m', 'apparent_temperature',
            'precipitation', 'rain', 'snowfall', 'wind_speed_10m']
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': start_date,
        'end_date': end_date,
        'timezone': 'auto',
        'hourly': info,
        'models': 'gfs05'}
    response = requests.get(url, params=params)
    hourly_data =  response.json()['hourly']
    hourly_data['time'] = pd.to_datetime(hourly_data['time'], format='%Y-%m-%dT%H:%M')
    hourly_data['Hora'] = hourly_data.pop('time')
    
    hourly_data['Temperatura'] = hourly_data.pop('temperature_2m')
    hourly_data['Sensação_térmica'] = hourly_data.pop('apparent_temperature')
    
    hourly_data['Precipitação_h'] = hourly_data.pop('precipitation')
    hourly_data['Chuva_mm'] = hourly_data.pop('rain')
    hourly_data['Neve_cm'] = hourly_data.pop('snowfall')
    hourly_data['Vento'] = hourly_data.pop('wind_speed_10m')
    
    df = pd.DataFrame(hourly_data)
    df = df.dropna(axis=0, how='any')
    df['Ano'] = pd.to_datetime(df['Hora']).dt.year
    df['Mes'] = pd.to_datetime(df['Hora']).dt.month
    df['Dia'] = pd.to_datetime(df['Hora']).dt.day
    df['Horário'] = pd.to_datetime(df['Hora']).dt.hour
    df['Data'] = pd.to_datetime(df['Hora']).dt.date
    
    keep_columns = ['Ano', 'Mes', 'Dia', 'Horário', 'Data', 'Hora',
                    'Temperatura', 'Sensação_térmica',
                    'Precipitação_h', 'Chuva_mm', 'Neve_cm', 'Vento']
    drop_columns = list(set(df.columns) - set(keep_columns))
    df = df.drop(columns=drop_columns)
    
    return df