import streamlit as st
import requests

API_SET = "http://127.0.0.1:8000/weather/set"
API_AUTO = "http://127.0.0.1:8000/weather/auto"

st.set_page_config(page_title="Smart Home - Sterowanie pogodą", layout="wide")

st.title("🛠 Panel sterowania pogodą")

st.write("Tutaj możesz ręcznie ustawiać parametry symulatora pogody albo przełączyć w tryb automatyczny.")

temp = st.slider("🌡 Temperatura [°C]", -20, 40, 20)
humidity = st.slider("💧 Wilgotność [%]", 0, 100, 50)
clouds = st.slider("☁️ Zachmurzenie [%]", 0, 100, 20)
sunlight = st.slider("🌞 Światło [lux]", 0, 50000, 20000)
wind = st.slider("💨 Wiatr [km/h]", 0, 150, 5)
precip = st.slider("🌧 Opady [mm]", 0, 100, 0)

col1, col2 = st.columns(2)

with col1:
    if st.button("📌 Zastosuj ręcznie"):
        try:
            requests.post(
                API_SET,
                json={
                    "temperature": temp,
                    "humidity": humidity,
                    "cloud_pct": clouds,
                    "sunlight_lux": sunlight,
                    "wind_kph": wind,
                    "precipitation_mm": precip,
                },
                timeout=2,
            )
            st.success("Parametry ustawione (ręczny tryb)!")
        except Exception as e:
            st.error(f"Błąd: {e}")

with col2:
    if st.button("🤖 Włącz tryb automatyczny"):
        try:
            requests.post(API_AUTO, timeout=2)
            st.success("Tryb automatyczny włączony!")
        except Exception as e:
            st.error(f"Błąd: {e}")
