import numpy as np
import requests
import streamlit as st

#cities_api_key = "6kJtGwr4zOzUffuJRSXZwhEhVG0j"
#weather_api_key = "aabc6ce5b9f965907122e09b02b1ac95"

@st.experimental_fragment()
def get_token():
    cities_api_key = "9fxIgrGxNnIChovLLn1yDll05cRT08ug"
    cities_secret = "HyQlPubKbHkUAtpm"
    
    token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    token_headers = { "Content-Type": "application/x-www-form-urlencoded" }
    token_data = {
        "grant_type": "client_credentials",
        "client_id": cities_api_key,
        "client_secret": cities_secret
    }
    response = requests.post(token_url, headers=token_headers, data=token_data)
    token = response.json()['access_token']
    return token

@st.experimental_fragment()
def get_cities(search_string):
    token = get_token()
    url = 'https://test.api.amadeus.com/v1/reference-data/locations/cities'
    headers = { 'accept': 'application/vnd.amadeus+json', 'Authorization': f'Bearer {token}' }
    params = { 'keyword': search_string, 'max': 5 }
    response = requests.get(url, headers=headers, params=params)
    return response.json()

@st.experimental_fragment()
def list_cities(search_string):
    cidades = []
    coordenadas = []
    
    data = get_cities(search_string)['data']
    for loc in range(len(data)):
        nome = data[loc]['name']
        if 'ZZZ' in data[loc]['address']['stateCode']:
            regiao = data[loc]['address']['countryCode']
        else:
            regiao = data[loc]['address']['stateCode']
        
        cidade = f"{nome}, {regiao}"
        lat = data[loc]['geoCode']['latitude']
        lon = data[loc]['geoCode']['longitude']
        
        cidades.append(cidade)
        coordenadas.append((lat, lon))
    
    result = list(zip(cidades, coordenadas))
    return result

@st.experimental_fragment()
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

st.title("Weather in cities")

lat = {}
lon = {}

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

with st.sidebar:
    searched_city = st.text_input("Pesquise uma cidade", key="searched_city")
    display_cities(searched_city)
    
    start_date = st.date_input("Escolha uma data inicial", value=None)
    end_date = st.date_input("Escolha uma data final", value=None) 

if st.sidebar.button(label="Buscar"):
    show_data()
else:
    st.write("Escolha uma cidade e data para começar!")


