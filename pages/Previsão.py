import numpy as np
import pandas as pd
import requests
import streamlit as st
from utils.time_tools import change_date_format
from utils.api_requests import get_cities, get_forecast
from utils.make_charts import make_chart

@st.experimental_fragment()
def display_city_options(searched_city):
    if searched_city:
        resultado = get_cities(searched_city)
        selected_city = st.radio("Cidades", options=[item[0] for item in resultado])
        lat = dict(resultado)[selected_city][0]
        lon = dict(resultado)[selected_city][1]
        
        final_result = [selected_city, lat, lon]
        
        return final_result

@st.experimental_fragment()
def temperature(data, rangebreaks):
    max_temp = np.max(np.array(data['Temperatura'])).round()
    min_temp = np.min(np.array(data['Temperatura'])).round()
    avg_temp = np.mean(np.array(data['Temperatura'])).round()
    avg_feel = np.mean(np.array(data['Sensação_térmica'])).round()
    
    st.markdown("#### Temperatura")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Máxima", f"{max_temp}ºC")
    col2.metric("Mínima", f"{min_temp}ºC")
    col3.metric("Temperatura média", f"{avg_temp}ºC")
    col4.metric("Sensação térmica", f"{avg_feel}ºC")
    
    #st.line_chart(data=data, y=['Máxima', 'Mínima'], color=['#911010', '#103b91'])
    st.plotly_chart(
        make_chart(type='line',
                   data=data,
                   x='Hora',
                   y=['Temperatura'],
                   ylabel='ºC',
                   color=['#103b91'],
                   rangebreaks=rangebreaks)
    )
    
@st.experimental_fragment()
def conditions(data, rangebreaks):
    avg_prec = np.mean(np.array(data['Precipitação_h'])).round()
    avg_rain = np.mean(np.array(data['Chuva_mm'])).round()
    avg_snow = np.mean(np.array(data['Neve_cm'])).round()
    avg_wind = np.mean(np.array(data['Vento'])).round()
    
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
                   x='Hora',
                   y=['Chuva_mm'],
                   ylabel='Volume',
                   color=['#103b91'],
                   rangebreaks=rangebreaks)
    )

@st.experimental_fragment()
def build_dashboard(data):
    dias = data['Dia'].unique()
    horarios = data['Horário'].unique()
    horas = data['Hora'].unique()
    
    col1, col2 = st.columns(2)
    filter_day = col1.multiselect("Dias", options=dias, placeholder="Selecione um dia")
    filter_hour = col2.multiselect("Horários", options=horarios, placeholder="Selecione um horário")
    
    if filter_day and filter_hour:
        filtered_data = data[(data['Dia'].isin(filter_day)) & (data['Horário'].isin(filter_hour))].reset_index(drop=True)
        include_times = filtered_data['Hora'].unique()
        rangebreaks = [dict(values=list(set(horas) - set(include_times)))]
    elif filter_day:
        filtered_data = data[data['Dia'].isin(filter_day)].reset_index(drop=True)
        include_times = filtered_data['Hora'].unique()
        rangebreaks = [dict(values=list(set(horas) - set(include_times)))]
    elif filter_hour:
        filtered_data = data[data['Horário'].isin(filter_hour)].reset_index(drop=True)
        include_times = filtered_data['Hora'].unique()
        rangebreaks = [dict(values=list(set(horas) - set(include_times)))]
    else:
        filtered_data = data
        rangebreaks = None

    temperature(filtered_data, rangebreaks=rangebreaks)
    conditions(filtered_data, rangebreaks=rangebreaks)
    st.dataframe(filtered_data, hide_index=True)

@st.experimental_fragment()
def main_container():
    hourly_data = get_forecast(lat, lon, start_date, end_date)
    st.markdown(f"**Cidade:** {selected_city}")
    st.markdown(f"**Período:** {change_date_format(start_date)} - {change_date_format(end_date)}")
    st.divider()

    build_dashboard(hourly_data)

st.set_page_config(
    page_title="Previsão do tempo",
    page_icon="📈",
)

st.title(f"Previsão do tempo")

with st.sidebar:
    searched_city = st.text_input("Pesquise uma cidade", key="searched_city")
    city_results = display_city_options(searched_city)
    
    if city_results:
        selected_city = city_results[0]
        lat = city_results[1]
        lon = city_results[2]
    
    col1, col2 = st.columns(2)
    start_date = col1.date_input("Data inicial", value=None, format="DD/MM/YYYY")
    end_date = col2.date_input("Data final", value=None, format="DD/MM/YYYY") 

if st.sidebar.button(label="Buscar"):
    main_container()
else:
    st.write("Escolha uma cidade e o período para começar!")