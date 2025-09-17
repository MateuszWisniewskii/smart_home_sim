import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")
st_autorefresh(interval=5000, key="refresh")

st.sidebar.title("🏠 Nawigacja")
page = st.sidebar.radio("Wybierz stronę:", ["Dashboard", "Rolety", "Światła"])

rooms = ["living_room", "bedroom", "kitchen"]

# ---------------------- DASHBOARD ----------------------
if page == "Dashboard":
    st.title("📊 Smart Home Dashboard")

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

    # ---------------- ROOMS STATE ----------------
    st.header("🪟💡 Stan pomieszczeń")
    try:
        state = requests.get(f"{API_URL}/smart_home", timeout=2).json()
    except Exception as e:
        st.error(f"Błąd w pobieraniu stanu domu: {e}")
        state = None

    if state:
        for room in rooms:
            st.subheader(room.replace("_", " ").title())
            col1, col2, col3 = st.columns(3)
            col1.metric("Pozycja rolety [%]", state["blinds"].get(room, 0))
            col2.metric("Kąt lameli [%]", state["slats"].get(room, 0))
            col3.metric("Jasność światła [%]", state["lights"].get(room, 0))
# ---------------------- ROLETA ----------------------
elif page == "Rolety":
    st.title("🪟 Sterowanie roletami")
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
        else:
            position = st.slider("Pozycja [%]", 0, 100, current_position, key=f"{room}_slider")
            if st.button(f"📌 Ustaw {room}", key=f"{room}_set"):
                requests.post(f"{API_URL}/smart_home/blinds/set", json={"room": room, "position": position})

# ---------------------- ŚWIATŁA ----------------------
elif page == "Światła":
    st.title("💡 Sterowanie światłami")
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
        else:
            brightness = st.slider("Jasność [%]", 0, 100, current_brightness, key=f"{room}_light_slider")
            if st.button(f"💡 Ustaw {room}", key=f"{room}_light_set"):
                requests.post(f"{API_URL}/smart_home/lights/set", json={"room": room, "brightness": brightness})
