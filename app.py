from flask import Flask, render_template, request, flash
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
from main import get_weather, get_cords, adjusted_distance
from typing import Optional, Dict



BASE_DIR = os.path.dirname(os.path.abspath(__file__))


app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
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

        # Convert stock distance safely
        try:
            stock_distance = float(stock_distance_raw) if stock_distance_raw else None
        except ValueError:
            flash("Stock distance must be a number.")
            stock_distance = None

        # Get coordinates and weather if city is provided
        coords = get_cords(city) if city else None
        if coords:
            latitude, longitude = coords
            weather = get_weather(latitude, longitude)
        else:
            flash("Could not find coordinates for the city.")

        # Handle actions
        if action == "update_weather":
            if not city:
                flash("Please enter a city to update weather.")
        elif action == "calculate":
            if not city:
                flash("Please enter a city.")
            elif stock_distance is None:
                flash("Please enter a valid stock distance.")
            elif not hitting_direction:
                flash("Please select a hitting direction.")
            elif weather:
                adjusted = adjusted_distance(stock_distance, hitting_direction, weather)
            else:
                flash("Weather data is missing or invalid.")

    return render_template(
        "index.html",
        city=city,
        stock_distance=stock_distance,
        hitting_direction=hitting_direction,
        weather=weather,
        adjusted=adjusted,
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
