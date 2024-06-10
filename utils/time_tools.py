from datetime import datetime, timedelta
import pandas as pd

def time_to_seconds(time_str):
    h, m = map(int, time_str.split(':'))
    return h * 3600 + m * 60

def seconds_to_time(seconds):
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{int(h):02}:{int(m):02}"

def estimated_time(times):
    total_seconds = sum(time_to_seconds(t) for t in times)
    average_seconds = total_seconds // len(times)
    return seconds_to_time(average_seconds)

def convert_to_hour_minutes(date_str):
    return datetime.strptime(date_str, '%Y-%m-%dT%H:%M').strftime('%H:%M')

def convert_date_format(date_str):
    return date_str.strftime('%d/%m/%Y')