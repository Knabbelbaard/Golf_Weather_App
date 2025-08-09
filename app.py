from flask import Flask, render_template, request
from main import get_weather, get_cords

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    weather = None
    city = "Enter city name"
    if request.method == 'POST':
        city = request.form.get('city')
        coords = get_cords(city)
        if coords:
            lat, lon = coords
            weather = get_weather(lat, lon)
    return render_template('index.html', weather=weather, city=city)

if __name__ == '__main__':
    app.run(debug=True)