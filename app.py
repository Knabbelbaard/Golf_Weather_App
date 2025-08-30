from flask import Flask, render_template, request, flash
import os
import logging
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from main import get_weather, get_cords, adjusted_distance, adjusted_for_temp
from typing import Optional, Dict



BASE_DIR = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

logging.basicConfig(level=logging.INFO)

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        city = ""
        stock_distance = None
        hitting_direction = None
        weather = None
        adjusted = None

        if request.method == "POST":
            action = request.form.get("action")
            city = (request.form.get("city") or "").strip()
            stock_distance_raw = (request.form.get("stock-distance") or "").strip()
            hitting_direction = request.form.get("hitting-direction") or None


            try:
                stock_distance = float(stock_distance_raw) if stock_distance_raw else None
            except ValueError:
                flash("Stock distance must be a number.")
                stock_distance = None


            coords = get_cords(city) if city else None
            if coords:
                latitude, longitude = coords
                weather = get_weather(latitude, longitude)
                if not weather:
                    logging.error(f"No weather data received for {city}")
            else:
                logging.error(f"Could not get coordinates for city {city}")
                flash("Could not find coordinates for the city.")
                

            if action == "calculate" and weather and stock_distance and hitting_direction:
                temp_adjusted = adjusted_for_temp(stock_distance, weather)
                if temp_adjusted:
                    adjusted = adjusted_distance(temp_adjusted["adjusted_for_temp"], hitting_direction, weather)

        return render_template(
            "index.html",
            city=city,
            stock_distance=stock_distance,
            hitting_direction=hitting_direction,
            weather=weather,
            temp_adjusted=temp_adjusted if 'temp_adjusted' in locals() else None,
            adjusted=adjusted,
        )

    except Exception as e:
        logging.exception("An error occured")
        return f"An error occured: {str(e)}", 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
