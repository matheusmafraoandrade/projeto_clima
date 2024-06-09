import numpy as np
import requests
import streamlit as st

def get_cities(search_string):
    url = 'https://geocoding-api.open-meteo.com/v1/search'
    params = { 'name': search_string, 'count': 5, 'language': 'pt', format: 'json' }
    response = requests.get(url, params=params)
    return response.json()

def list_cities(search_string):
    cidades = []
    coordenadas = []
    
    data = get_cities(search_string)['results']
    for city in range(len(data)):
        name = data[city]['name']
        region = data[city]['admin1']
        country = data[city]['country']
        
        cidade = f"{name}, {region}, {country}"
        lat = data[city]['latitude']
        lon = data[city]['longitude']
        
        cidades.append(cidade)
        coordenadas.append((lat, lon))
    
    result = list(zip(cidades, coordenadas))
    return result

def get_weather(lat, lon, start_date, end_date):
    url = 'https://archive-api.open-meteo.com/v1/era5'
    info = ['temperature_2m_max', 'temperature_2m_min', 'rain_sum', 'snowfall_sum', 'sunshine_duration']
    params = {
        'latitude': lat,
        'longitude': lon,
        'start_date': start_date,
        'end_date': end_date,
        'daily': info }
    response = requests.get(url, params=params)
    return response.json()

@st.experimental_fragment()
def display_cities(searched_city):
    if searched_city:
        resultado = list_cities(searched_city)
        selected_city = st.radio("Cidades", options=[item[0] for item in resultado])
        
        globals()['lat'] = dict(resultado)[selected_city][0]
        globals()['lon'] = dict(resultado)[selected_city][1]
        
        return selected_city
    
@st.experimental_fragment()
def show_data():
    tempo = get_weather(lat, lon, start_date, end_date)
    
    max = np.max(np.array(tempo['daily']['temperature_2m_max'])).round(2)
    min = np.min(np.array(tempo['daily']['temperature_2m_min'])).round(2)
    avg_rain = np.mean(np.array(tempo['daily']['rain_sum'])).round(2)
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        col1.metric("Máxima", f"{max}ºC")
        col2.metric("Mínima", f"{min}ºC")
        col3.metric("Chuva", f"{avg_rain:.2f} mm")
        
        df = st.dataframe(tempo['daily'])

st.title("Weather in cities")

lat = {}
lon = {}

with st.sidebar:
    searched_city = st.text_input("Pesquise uma cidade", key="searched_city")
    display_cities(searched_city)
    
    start_date = st.date_input("Escolha uma data inicial", value=None)
    end_date = st.date_input("Escolha uma data final", value=None) 

with st.container():
    if st.sidebar.button(label="Buscar"):
        show_data()
    else:
        st.write("Escolha uma cidade e data para começar!")


