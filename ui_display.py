import streamlit as st
import requests
import random
from streamlit_autorefresh import st_autorefresh

API_URL = "http://127.0.0.1:8000/weather"

st.set_page_config(page_title="Smart Home - Podgląd", layout="wide")

# auto-refresh co 5 sek
st_autorefresh(interval=5000, key="refresh")

st.title("🏠 Smart Home Dashboard - Podgląd")

# ---------------- WEATHER ----------------
st.header("🌦 Pogoda (z symulatora)")

try:
    weather = requests.get(API_URL, timeout=2).json()
except Exception as e:
    st.error(f"Błąd w pobieraniu pogody: {e}")
    weather = None

if weather:
    st.subheader(f"🕒 Aktualna godzina symulacji: {weather['time']}")

if weather:
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡 Temperatura [°C]", weather["temperature"])
    col2.metric("💧 Wilgotność [%]", weather["humidity"])
    col3.metric("💨 Wiatr [km/h]", weather["wind_kph"])

    col4, col5, col6 = st.columns(3)
    col4.metric("☁️ Zachmurzenie [%]", weather["cloud_pct"])
    col5.metric("🌞 Światło [lux]", weather["sunlight_lux"])
    col6.metric("🌧 Opady [mm]", weather["precipitation_mm"])

    # ---------------- TEMPERATURE SENSORS ----------------
    st.subheader("🌡 Temperatury z różnych stron domu")

    base_temp = weather["temperature"]

    temps = {
        "Północ": base_temp - random.uniform(1.0, 2.5),
        "Południe": base_temp + random.uniform(1.0, 3.0),
        "Wschód": base_temp + random.uniform(-1.0, 1.5),
        "Zachód": base_temp + random.uniform(-1.0, 1.5),
        "Wewnątrz": base_temp + random.uniform(-0.5, 0.5),
    }

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🌡 Północ", round(temps["Północ"], 1))
    c2.metric("🌡 Południe", round(temps["Południe"], 1))
    c3.metric("🌡 Wschód", round(temps["Wschód"], 1))
    c4.metric("🌡 Zachód", round(temps["Zachód"], 1))
    c5.metric("🏠 Wewnątrz", round(temps["Wewnątrz"], 1))

    # ---------------- ROOMS ----------------
    st.header("🏠 Pokoje i czujniki")

    rooms = ["Pokój dziecka 1", "Pokój dziecka 2", "Salon", "Sypialnia", "Kuchnia", "Łazienka"]
    tabs = st.tabs(rooms)

    for i, room in enumerate(rooms):
        with tabs[i]:
            st.subheader(room)

            # Symulacja danych dla danego pokoju
            room_temp = weather["temperature"] + random.uniform(-2, 2)
            room_hum = weather["humidity"] + random.uniform(-5, 5)

            col1, col2 = st.columns(2)
            col1.metric("🌡 Temperatura [°C]", round(room_temp, 1))
            col2.metric("💧 Wilgotność [%]", round(room_hum, 1))

            st.write("💡 Oświetlenie: sterowane w systemie")
            st.write("🚪 Drzwi: sterowane w systemie")
