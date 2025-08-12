from flask import Flask, render_template, request
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from main import get_weather, get_cords, adjusted_distance


load_dotenv()



BASE_DIR = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    city = "Enter city name"

    stock_distance: Optional[float] = None
    hitting_direction: Optional[str] = None
    adjusted: Optional[Dict[str, Any]] = None
    if request.method == 'POST':
        posted_city = request.form.get('city')
        if posted_city:
            city = posted_city
        if city and city != "Enter city name":
            coords = get_cords(city)
            if coords:
                lat, lon = coords
                weather = get_weather(lat, lon)
    stock_distance_raw: Optional[str] = request.form.get('stock-distance')
    hitting_direction = request.form.get('hitting-direction')

    if stock_distance_raw is not None and stock_distance_raw.strip() != "":
        try:
            stock_distance = float(stock_distance_raw)
        except ValueError:
            stock_distance = None

    if weather and stock_distance is not None and hitting_direction:
        adjusted = adjusted_distance(stock_distance, hitting_direction, weather)

    return render_template(
        'index.html',
        weather=weather,
        city=city,
        stock_distance=stock_distance,
        hitting_direction=hitting_direction,
        adjusted=adjusted)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
