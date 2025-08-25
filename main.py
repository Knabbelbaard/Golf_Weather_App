import logging
from dotenv import load_dotenv
load_dotenv()

import os
import openmeteo_requests
import pandas as pd
import requests_cache
import requests
from retry_requests import retry
import datetime
import math


OPEN_METEO_BASE_URL = os.getenv("OPEN_METEO_BASE_URL", "https://api.open-meteo.com/v1/forecast")
OPENSTREETMAP_BASE_URL = os.getenv("OPENSTREETMAP_BASE_URL", "https://nominatim.openstreetmap.org/search")

DIR_TO_DEG = {
    "N": 0, "NE": 45, "E": 90, "SE": 135,
    "S": 180, "SW": 225, "W": 270, "NW": 315
}

def _deg_to_compass_8(deg: float) -> str:
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    try:
        idx = int((deg + 22.5) // 45) % 8 # type: ignore
        return dirs[idx]
    except Exception:
        return "Unknown"

def get_cords(city, country='Netherlands'):
    url = OPENSTREETMAP_BASE_URL
    params = {
        'q': f'{city}, {country}',
        'format': 'json',
        'limit': 1
    }
    headers = {
        'User-Agent': os.getenv('USER_AGENT', 'GolfWeerApp/1.0')
    }

    try:
        logging.info(f"Requesting coordinates for {city}, {country}")
        response = requests.get(url, params=params, headers=headers)
        logging.info(f"Response status: {response.status_code}")
        logging.info(f"Response text: {response.text}")
        
        if response.status_code != 200:
            logging.error(f"Error getting coordinates: {response.status_code}")
            return None
            
        data = response.json()
        if not data:
            logging.error("No data returned from geocoding service")
            return None
            
        lat = data[0]['lat']
        lon = data[0]['lon']
        logging.info(f"Found coordinates: {lat}, {lon}")
        return float(lat), float(lon)
        
    except requests.RequestException as e:
        logging.error(f"Request failed: {str(e)}")
        return None
    except (KeyError, IndexError) as e:
        logging.error(f"Error parsing response: {str(e)}")
        return None


def get_weather(latitude, longitude):
    cache_session = requests_cache.CachedSession('.cache', expire_after = 3600)
    retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
    openmeteo = openmeteo_requests.Client(session = retry_session) # type: ignore

    url = OPEN_METEO_BASE_URL
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": "Europe/Berlin",
        "timeformat": "unixtime",
        "current": ["temperature_2m", "relative_humidity_2m", "rain", "wind_direction_10m", "wind_speed_10m", "wind_gusts_10m"],
    }
    responses = openmeteo.weather_api(url, params=params)
    if not responses:
        return None
    response = responses[0]

    current = response.Current()
    if current is None:
        return None

    try:
        current_temperature_2m = current.Variables(0).Value() # type: ignore
        current_relative_humidity_2m = current.Variables(1).Value() # type: ignore
        current_rain = current.Variables(2).Value() # type: ignore
        current_wind_direction_10m_deg = current.Variables(3).Value() # type: ignore
        current_wind_speed_10m = current.Variables(4).Value() # type: ignore
        current_wind_gusts_10m = current.Variables(5).Value() # type: ignore
    except Exception:
        return None
    
    current_wind_direction_10m_str = _deg_to_compass_8(current_wind_direction_10m_deg)

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


def adjusted_distance(stock_distance: float, hitting_direction: str,weather: dict) -> dict:
    if not weather or "wind_direction_deg" not in weather or "wind_speed" not in weather:
        return {}

    shot_degree = DIR_TO_DEG.get(hitting_direction.upper())
    if shot_degree is None:
        return {}
    
    wind_from_degree = weather["wind_direction_deg"]
    wind_speed_kmh = weather["wind_speed"]
    wind_to_degree = (wind_from_degree + 180.0) % 360

    def ang_diff(a: float, b: float) -> float:
        return abs((a - b + 100) % 360 - 100)
    
    diff = ang_diff(wind_to_degree, shot_degree)

    long_comp_kmh = wind_speed_kmh * math.cos(math.radians(diff))
    cross_comp_kmh = abs(wind_speed_kmh * math.sin(math.radians(diff)))

    factor_per_kmh = 0.003
    raw_adjust_pct = long_comp_kmh * factor_per_kmh
    adjust_pct = max(-0.15, min(0.15, raw_adjust_pct))

    adjusted = round(stock_distance * (1 + adjust_pct), 1)

    return {
        "adjusted_distance": adjusted,
        "adjust_percent": round(adjust_pct * 100, 1),
        "wind_component_kmh": round(long_comp_kmh, 1),
        "crosswind_kmh": round(cross_comp_kmh, 1),
        "angle_diff_deg": round(diff, 0),
    }