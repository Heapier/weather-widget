from datetime import datetime

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request

load_dotenv()  # Memuat variabel lingkungan dari file .env

app = Flask(__name__, template_folder="templates")

def get_weather_data(query="Semarang"):
    # URL API untuk mendapatkan data cuaca
    url = "https://api.weatherapi.com/v1/forecast.json"
    # Parameter yang dibutuhkan oleh API
    params = {
        # Mengambil kunci API dari environment variable
        "key": "",  # Isi dengan kunci API
        "q": query,
        "days": 5,
        "aqi": "no",
        "alerts": "no",
    }
    try:
        # Melakukan request ke API
        r = requests.get(url, params=params)
        r.raise_for_status()  # Jika respons tidak berhasil, akan menimbulkan HTTPError
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
        return None
    except requests.exceptions.RequestException as err:
        print(f"Error occurred: {err}")
        return None

    try:
        # Mengembalikan data dalam bentuk JSON
        return r.json()
    except ValueError:
        print("Error: Unable to parse JSON response")
        return None


def process_data(location):
    # Mendapatkan data cuaca dari lokasi yang diberikan
    weather = get_weather_data(location)
    data = {}

    # Jika data cuaca tidak valid, keluar dan kembalikan None
    if weather is None or not isinstance(weather, dict):
        print("Error: Unable to process weather data")
        return None

    try:
        # Mengubah format waktu dari data cuaca
        d = datetime.strptime(
            weather["current"]["last_updated"], "%Y-%m-%d %H:%M")
        # Memperbarui data dengan informasi lokasi dan cuaca saat ini
        data.update({
            "location": {
                "name": weather["location"]["name"],
                "country": weather["location"]["country"],
            },
            "current": {
                "temp": weather["current"]["temp_c"],
                "condition": {
                    "text": weather["current"]["condition"]["text"],
                    "icon": weather["current"]["condition"]["icon"],
                },
                "datetime": {
                    "day": d.strftime("%A"),
                    "date": d.strftime("%d %B %Y"),
                },
            }
        })

        # Mempersiapkan daftar untuk ramalan cuaca
        forecast = []

        # Mengubah format waktu dan memperbarui ramalan cuaca untuk setiap hari
        for i in weather["forecast"]["forecastday"]:
            d = datetime.strptime(i["date"], "%Y-%m-%d")

            forecast.append({
                "datetime": {
                    "day": d.strftime("%A"),
                    "date": d.strftime("%d %B %Y"),
                },
                "condition": {
                    "text": i["day"]["condition"]["text"],
                    "icon": i["day"]["condition"]["icon"],
                },
                "temp": {
                    "avgtemp": i["day"]["avgtemp_c"],
                    "mintemp": i["day"]["mintemp_c"],
                    "maxtemp": i["day"]["maxtemp_c"],
                }
            })

        # Menambahkan forecast ke data
        data.update({"forecast": forecast})

    except KeyError as e:
        # Menangani kesalahan jika kunci tidak ditemukan dalam data cuaca
        print(f"Error: Key {e} not found in weather data")
        return None

    return data


@app.route("/", methods=["GET", "POST"])
def index():
    # Mendapatkan lokasi dari form, atau menggunakan 'Semarang' sebagai default
    location = request.form.get("location", "Semarang").strip()

    # Jika lokasi kosong, gunakan 'Semarang' sebagai lokasi
    if location == "":
        location = "Semarang"

    # Mendapatkan data cuaca untuk lokasi yang diberikan
    weather_data = process_data(location)

    # Merender template dengan data cuaca
    return render_template("index.html", data=weather_data)
