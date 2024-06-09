import numpy as np
import streamlit as st
from datetime import datetime
from utils.time_tools import estimated_time, convert_to_hour_minutes, convert_date_format
from utils.api_requests import get_cities, get_weather

@st.experimental_fragment()
def display_city_options(searched_city):
    if searched_city:
        resultado = get_cities(searched_city)
        selected_city = st.radio("Cidades", options=[item[0] for item in resultado])
        
        globals()['lat'] = dict(resultado)[selected_city][0]
        globals()['lon'] = dict(resultado)[selected_city][1]
        
        return selected_city

@st.experimental_fragment()
def temperature(daily_data):
    max_temp = np.max(np.array(daily_data['Máxima'])).round()
    min_temp = np.min(np.array(daily_data['Mínima'])).round()
    avg_temp = np.mean(np.array([daily_data['Máxima'], daily_data['Mínima']])).round()
    
    st.markdown("#### Temperatura")
    col1, col2, col3 = st.columns(3)
    col1.metric("Máxima", f"{max_temp}ºC")
    col2.metric("Mínima", f"{min_temp}ºC")
    col3.metric("Média", f"{avg_temp}ºC")
    
    st.line_chart(data=daily_data, x='Data', y=['Máxima', 'Mínima'], color=['#911010', '#103b91'])
    
@st.experimental_fragment()
def conditions(daily_data):
    avg_rain = np.mean(np.array(daily_data['Chuva_mm'])).round()
    avg_snow = np.mean(np.array(daily_data['Neve_cm'])).round()
    avg_prec = np.mean(np.array(daily_data['Precipitação_h'])).round()
    avg_wind = np.mean(np.array(daily_data['Vento_max'])).round()
    
    st.markdown("#### Condições diárias")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Horas de chuva", f"{avg_prec} h")
    col2.metric("Chuva", f"{avg_rain} mm")
    col3.metric("Neve", f"{avg_snow} cm")
    col4.metric("Vento", f"{avg_wind} km/h")
    
@st.experimental_fragment()
def sunlight(daily_data):
    avg_sun = np.mean(np.array(daily_data['Horas_sol'])).round()
    sunrise = estimated_time(list(daily_data['Nascer_do_sol']))
    sunset = estimated_time(list(daily_data['Por_do_sol']))
    
    st.markdown("#### Luz do sol")
    col1, col2, col3 = st.columns(3)
    col1.metric("Horas de sol", f"{avg_sun} h")
    col2.metric("Nascer do sol aproximado", sunrise)
    col3.metric("Pôr do sol aproximado", sunset)

st.title(f"Dados climáticos")

lat = {}
lon = {}

with st.sidebar:
    searched_city = st.text_input("Pesquise uma cidade", key="searched_city")
    selected_city = display_city_options(searched_city)
    
    start_date = st.date_input("Escolha uma data inicial", value=None)
    end_date = st.date_input("Escolha uma data final", value=None) 

with st.container():
    if st.sidebar.button(label="Buscar"):
        daily_data = get_weather(lat, lon, start_date, end_date)
        st.markdown(f"##### Cidade: {selected_city}")
        st.markdown(f"##### Período: {convert_date_format(start_date)} - {convert_date_format(end_date)}")
        
        temperature(daily_data)
        conditions(daily_data)
        sunlight(daily_data)
        st.dataframe(daily_data)
    else:
        st.write("Escolha uma cidade e data para começar!")


