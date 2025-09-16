import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Home - Sterowanie pogodą", layout="wide")

st.title("🛠 Panel sterowania pogodą")

st.write("Tutaj możesz ręcznie ustawiać parametry symulatora pogody oraz sterować czasem symulacji.")

# ------------------- WEATHER CONTROL -------------------
st.header("🌦 Ustaw parametry pogody")

temp = st.slider("🌡 Temperatura [°C]", -20, 40, 20)
humidity = st.slider("💧 Wilgotność [%]", 0, 100, 50)
clouds = st.slider("☁️ Zachmurzenie [%]", 0, 100, 20)
sunlight = st.slider("🌞 Światło [lux]", 0, 50000, 20000)
wind = st.slider("💨 Wiatr [km/h]", 0, 150, 5)
precip = st.slider("🌧 Opady [mm]", 0, 100, 0)

if st.button("📌 Zastosuj parametry"):
    try:
        r = requests.post(
            f"{API_URL}/weather/set",
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
        if r.status_code == 200:
            st.success("Parametry ustawione ✅")
        else:
            st.error(f"Błąd API: {r.text}")
    except Exception as e:
        st.error(f"Błąd: {e}")

# ------------------- TIME CONTROL -------------------
st.header("🕒 Sterowanie czasem symulacji")

col1, col2 = st.columns(2)

with col1:
    time_input = st.time_input("Ustaw godzinę")
    if st.button("📌 Ustaw czas"):
        try:
            r = requests.post(
                f"{API_URL}/weather/time/set",
                json={"hour": time_input.hour, "minute": time_input.minute},
                timeout=2,
            )
            if r.status_code == 200:
                st.success(f"Czas ustawiony na {r.json()['time']} ✅")
            else:
                st.error(f"Błąd API: {r.text}")
        except Exception as e:
            st.error(f"Błąd: {e}")

