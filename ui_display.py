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
# ---------------- BLINDS ----------------
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

# ---------------- LIGHTS ----------------
st.header("💡 Sterowanie światłami (0-100%)")

for room in rooms:
    st.subheader(room.replace("_", " ").title())

    try:
        state = requests.get(f"{API_URL}/smart_home", timeout=2).json()
        current_brightness = state["lights"].get(room, 0)
        light_blocked = state.get("light_limit_active", False)
    except:
        current_brightness = 0
        light_blocked = False

    if light_blocked:
        st.warning("⚠️ Jasność ograniczona przy dużym nasłonecznieniu")
        st.slider("Jasność [%]", 0, 100, current_brightness, key=f"{room}_light_slider", disabled=True)
        st.button(f"💡 Ustaw {room}", key=f"{room}_light_set", disabled=True)
        col1, col2 = st.columns(2)
        with col1:
            st.button("⬆ +10%", key=f"{room}_light_up", disabled=True)
        with col2:
            st.button("⬇ -10%", key=f"{room}_light_down", disabled=True)
    else:
        brightness = st.slider("Jasność [%]", 0, 100, current_brightness, key=f"{room}_light_slider")
        #print(f"{room}:{brightness}")
        if st.button(f"💡 Ustaw {room}", key=f"{room}_light_set"):
            requests.post(f"{API_URL}/smart_home/lights/set", json={"room": room, "brightness": brightness})

        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬆ +10%", key=f"{room}_light_up"):
                requests.post(f"{API_URL}/smart_home/lights/adjust", json={"room": room, "delta": 10})
        with col2:
            if st.button("⬇ -10%", key=f"{room}_light_down"):
                requests.post(f"{API_URL}/smart_home/lights/adjust", json={"room": room, "delta": -10})

        st.write(f"Aktualna jasność: {current_brightness}%")

# ---------------- AIR CONDITIONING ----------------
st.header("❄️ Sterowanie klimatyzacją")

for room in rooms:
    st.subheader(room.replace("_", " ").title())

    try:
        state = requests.get(f"{API_URL}/smart_home", timeout=2).json()
        ac_on = state["ac"].get(room, False)
        ac_auto = state.get("ac_auto_active", False)
    except:
        ac_on = False
        ac_auto = False

    if ac_auto:
        st.info("ℹ️ Klimatyzacja automatycznie włączona (temp. > 35°C) – możesz ją wyłączyć ręcznie.")

    ac_state = st.toggle("Klimatyzacja", value=ac_on, key=f"{room}_ac")
    if st.button(f"📌 Zmień AC {room}", key=f"{room}_ac_set"):
        requests.post(f"{API_URL}/smart_home/ac/set", json={"room": room, "state": ac_state})