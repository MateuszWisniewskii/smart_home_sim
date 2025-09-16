import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

# auto-refresh co 5 sek
st_autorefresh(interval=5000, key="refresh")

st.title("🏠 Smart Home Dashboard")

# ---------------- WEATHER STATE ----------------
st.header("🌦 Aktualna pogoda")
try:
    weather = requests.get(f"{API_URL}/weather", timeout=2).json()
    st.success("Dane pobrane z API ✅")
except Exception as e:
    st.error(f"Błąd w pobieraniu pogody: {e}")
    weather = None

if weather:
    st.subheader(f"🕒 Czas symulacji: {weather['time']}")
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡 Temperatura [°C]", weather["temperature"])
    col2.metric("💧 Wilgotność [%]", weather["humidity"])
    col3.metric("💨 Wiatr [km/h]", weather["wind_kph"])

    col4, col5, col6 = st.columns(3)
    col4.metric("☁️ Zachmurzenie [%]", weather["cloud_pct"])
    col5.metric("🌞 Światło [lux]", weather["sunlight_lux"])
    col6.metric("🌧 Opady [mm]", weather["precipitation_mm"])

st.header("🪟 Sterowanie roletami (0-100%)")

rooms = ["living_room", "bedroom", "kitchen"]  

for room in rooms:
    st.subheader(room.replace("_", " ").title())

    try:
        state = requests.get(f"{API_URL}/smart_home", timeout=2).json()
        current_position = state["blinds"].get(room, 0)
        blocked = state.get("wind_limit_active", False)
    except:
        current_position = 0
        blocked = False

    if blocked:
        st.warning("⚠️ Rolety zablokowane przy wietrze > 80 km/h")
        st.slider("Pozycja [%]", 0, 100, current_position, key=f"{room}_slider", disabled=True)
        st.button("📌 Ustaw", key=f"{room}_set", disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.button("⬆ +10%", key=f"{room}_up", disabled=True)
        with col2:
            st.button("⬇ -10%", key=f"{room}_down", disabled=True)
    else:
        # normalne sterowanie suwakiem i przyciskami
        position = st.slider("Pozycja [%]", 0, 100, current_position, key=f"{room}_slider")
        if st.button(f"📌 Ustaw {room}", key=f"{room}_set"):
            requests.post(f"{API_URL}/smart_home/blinds/set", json={"room": room, "position": position})

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬆ +10%", key=f"{room}_up"):
                requests.post(f"{API_URL}/smart_home/blinds/adjust", json={"room": room, "delta": 10})
        with col2:
            if st.button("⬇ -10%", key=f"{room}_down"):
                requests.post(f"{API_URL}/smart_home/blinds/adjust", json={"room": room, "delta": -10})

    st.write(f"Aktualna pozycja: {current_position}%")
