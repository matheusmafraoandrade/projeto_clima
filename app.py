import numpy as np
import streamlit as st
from datetime import datetime
from utils.time_tools import estimated_time, convert_date_format
from utils.api_requests import get_cities, get_weather
from utils.make_charts import make_chart

@st.experimental_fragment()
def display_city_options(searched_city):
    if searched_city:
        resultado = get_cities(searched_city)
        selected_city = st.radio("Cidades", options=[item[0] for item in resultado])
        
        globals()['lat'] = dict(resultado)[selected_city][0]
        globals()['lon'] = dict(resultado)[selected_city][1]
        
        return selected_city

@st.experimental_fragment()
def temperature(data, rangebreaks):
    max_temp = np.max(np.array(data['Máxima'])).round()
    min_temp = np.min(np.array(data['Mínima'])).round()
    avg_temp = np.mean(np.array([data['Máxima'], data['Mínima']])).round()
    
    st.markdown("#### Temperatura")
    col1, col2, col3 = st.columns(3)
    col1.metric("Máxima", f"{max_temp}ºC")
    col2.metric("Mínima", f"{min_temp}ºC")
    col3.metric("Média", f"{avg_temp}ºC")
    
    #st.line_chart(data=data, y=['Máxima', 'Mínima'], color=['#911010', '#103b91'])
    st.plotly_chart(
        make_chart(type='line',
                   data=data,
                   y=['Máxima', 'Mínima'],
                   ylabel='ºC',
                   color=['#911010', '#103b91'],
                   rangebreaks=rangebreaks)
    )
    
@st.experimental_fragment()
def conditions(data, rangebreaks):
    avg_prec = np.mean(np.array(data['Precipitação_h'])).round()
    avg_rain = np.mean(np.array(data['Chuva_mm'])).round()
    avg_snow = np.mean(np.array(data['Neve_cm'])).round()
    avg_wind = np.mean(np.array(data['Vento_max'])).round()
    
    st.markdown("#### Condições diárias")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Horas de chuva", f"{avg_prec} h")
    col2.metric("Volume de chuva", f"{avg_rain} mm")
    col3.metric("Neve", f"{avg_snow} cm")
    col4.metric("Vento", f"{avg_wind} km/h")
    
    #st.bar_chart(data=data, y=['Chuva_mm', 'Neve_cm'])
    st.plotly_chart(
        make_chart(type='line',
                   data=data,
                   y=['Chuva_mm'],
                   ylabel='Volume',
                   color=['#103b91'],
                   rangebreaks=rangebreaks)
    )
    
@st.experimental_fragment()
def sunlight(data):
    avg_sun = np.mean(np.array(data['Horas_sol'])).round()
    sunrise = estimated_time(data['Nascer_do_sol'])
    sunset = estimated_time(data['Por_do_sol'])
    
    st.markdown("#### Luz do sol")
    col1, col2, col3 = st.columns(3)
    col1.metric("Horas de sol", f"{avg_sun} h")
    col2.metric("Nascer do sol aproximado", sunrise)
    col3.metric("Pôr do sol aproximado", sunset)

@st.experimental_fragment()
def build_dashboard(data):
    anos = data['Ano'].unique()
    meses = data['Mes'].unique()
    datas = data['Data'].unique()
    
    col1, col2 = st.columns(2)
    filter_year = col1.multiselect("Anos", options=anos, placeholder="Selecione um ano")
    filter_month = col2.multiselect("Meses", options=meses, placeholder="Selecione um mês")
    
    if filter_year and filter_month:
        filtered_data = data[(data['Ano'].isin(filter_year)) & (data['Mes'].isin(filter_month))].reset_index(drop=True)
        include_dates = filtered_data['Data'].unique()
        rangebreaks = [dict(values=list(set(datas) - set(include_dates)))]
    elif filter_year:
        filtered_data = data[data['Ano'].isin(filter_year)].reset_index(drop=True)
        include_dates = filtered_data['Data'].unique()
        rangebreaks = [dict(values=list(set(datas) - set(include_dates)))]
    elif filter_month:
        filtered_data = data[data['Mes'].isin(filter_month)].reset_index(drop=True)
        include_dates = filtered_data['Data'].unique()
        rangebreaks = [dict(values=list(set(datas) - set(include_dates)))]
    else:
        filtered_data = data
        rangebreaks = None

    temperature(filtered_data, rangebreaks=rangebreaks)
    conditions(filtered_data, rangebreaks=rangebreaks)
    sunlight(filtered_data)
    st.dataframe(filtered_data, hide_index=True)

@st.experimental_fragment()
def main_container():
    daily_data = get_weather(lat, lon, start_date, end_date)
    st.markdown(f"**Cidade:** {selected_city}")
    st.markdown(f"**Período:** {convert_date_format(start_date)} - {convert_date_format(end_date)}")
    st.divider()

    build_dashboard(daily_data)

st.title(f"Dados climáticos")

lat = {}
lon = {}

with st.sidebar:
    searched_city = st.text_input("Pesquise uma cidade", key="searched_city")
    selected_city = display_city_options(searched_city)
    
    start_date = st.date_input("Escolha uma data inicial", value=None, format="DD/MM/YYYY")
    end_date = st.date_input("Escolha uma data final", value=None, format="DD/MM/YYYY") 

if st.sidebar.button(label="Buscar"):
    main_container()
else:
    st.write("Escolha uma cidade e data para começar!")




