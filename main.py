import openmeteo_requests
import pandas as pd
import requests_cache
import requests
from retry_requests import retry
import datetime

def get_cords(city, country='Netherlands'):
    url = f'https://nominatim.openstreetmap.org/search'
    params = {
        'q': f'{city}, {country}',
        'format': 'json',
        'limit': 1
    }
    headers = {'User-Agent': 'YourAppName/1.0 (your.email@example.com)'}
    
    response = requests.get(url, params=params, headers=headers)
    data = response.json()
    
    if data:
        lat = data[0]['lat']
        lon = data[0]['lon']
        return float(lat), float(lon)
    else:
        return None


def get_weather(latitude, longitude):
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session) # type: ignore

    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "Europe/Berlin",
        "timeformat": "unixtime",
        "current": ["temperature_2m", "relative_humidity_2m", "rain", "wind_direction_10m", "wind_speed_10m", "wind_gusts_10m"],
    }
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    current = response.Current()
    if current is None:
        return None

    current_temperature_2m = current.Variables(0).Value() # type: ignore
    current_relative_humidity_2m = current.Variables(1).Value() # type: ignore
    current_rain = current.Variables(2).Value() # type: ignore
    current_wind_direction_10m_deg = current.Variables(3).Value() # type: ignore
    if 0 <= current_wind_direction_10m_deg < 45:
        current_wind_direction_10m_str = "NE"
    elif 45 <= current_wind_direction_10m_deg < 90:
        current_wind_direction_10m_str = "E"
    elif 90 <= current_wind_direction_10m_deg < 135:
        current_wind_direction_10m_str = "SE"
    elif 135 <= current_wind_direction_10m_deg < 180:
        current_wind_direction_10m_str = "S"
    elif 180 <= current_wind_direction_10m_deg < 225:
        current_wind_direction_10m_str = "SW"
    elif 225 <= current_wind_direction_10m_deg < 270:
        current_wind_direction_10m_str = "W"
    elif 270 <= current_wind_direction_10m_deg < 315:
        current_wind_direction_10m_str = "NW"
    elif 315 <= current_wind_direction_10m_deg < 360:
        current_wind_direction_10m_str = "N"
    else:
        current_wind_direction_10m_str = "Unknown"
    current_wind_speed_10m = current.Variables(4).Value() # type: ignore
    current_wind_gusts_10m = current.Variables(5).Value() # type: ignore

    timestamp = current.Time() # type: ignore
    local_time = datetime.datetime.fromtimestamp(timestamp, datetime.timezone.utc).astimezone(datetime.timezone(datetime.timedelta(hours=2)))

    return {
        "temperature": round(current_temperature_2m, 1),
        "humidity": round(current_relative_humidity_2m, 1),
        "rain": round(current_rain, 1),
        "wind_direction_str": current_wind_direction_10m_str,
        "wind_direction_deg": round(current_wind_direction_10m_deg, 1),
        "wind_speed": round(current_wind_speed_10m, 1),
        "wind_gust": round(current_wind_gusts_10m, 1),
        "time": local_time.strftime("%Y-%m-%d %H:%M:%S"),
    }

def adjusted_distance():
    pass