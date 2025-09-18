import streamlit as st
import requests
import random
from datetime import datetime

API_URL_WEATHER = "http://127.0.0.1:8000/weather"
API_URL_SMART_HOME = "http://127.0.0.1:8000/smart_home"

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")
st.title("🏠 Smart Home Dashboard")

# ---------------- MANUAL WEATHER CONTROL ----------------
st.sidebar.header("🛠 Sterowanie pogodą")
temp = st.sidebar.slider("Temperatura [°C]", -20, 40, 20)
humidity = st.sidebar.slider("Wilgotność [%]", 0, 100, 50)
clouds = st.sidebar.slider("Zachmurzenie [%]", 0, 100, 20)
sunlight = st.sidebar.slider("Światło [lux]", 0, 50000, 20000)
wind = st.sidebar.slider("Wiatr [km/h]", 0, 150, 5)
precip = st.sidebar.slider("Opady [mm]", 0, 100, 0)

if st.sidebar.button("Zastosuj ręcznie"):
    try:
        requests.post(
            f"{API_URL_WEATHER}/set",
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
        st.sidebar.success("Parametry ustawione (ręczny tryb)!")
    except Exception as e:
        st.sidebar.error(f"Błąd: {e}")

# ---------------- WEATHER ----------------
st.header("🌦 Pogoda (z symulatora)")
try:
    weather = requests.get(API_URL_WEATHER, timeout=2).json()
except Exception as e:
    st.error(f"Błąd w pobieraniu pogody: {e}")
    weather = None

if weather:
    col1, col2, col3 = st.columns(3)
    col1.metric("🌡 Temperatura [°C]", weather["temperature"])
    col2.metric("💧 Wilgotność [%]", weather["humidity"])
    col3.metric("💨 Wiatr [km/h]", weather["wind_kph"])

    col4, col5, col6 = st.columns(3)
    col4.metric("☁️ Zachmurzenie [%]", weather["cloud_pct"])
    col5.metric("🌞 Światło [lux]", weather["sunlight_lux"])
    col6.metric("🌧 Opady [mm]", weather["precipitation_mm"])

# ---------------- VENTILATION / VOC ----------------
st.header("🌬 Wentylacja (VOC)")

if "ventilation" not in st.session_state:
    # Pobieramy aktualny stan wentylacji z API
    try:
        vent_state = requests.get(f"{API_URL_SMART_HOME}/ventilation", timeout=2).json()
        st.session_state.ventilation = vent_state.get("ventilation_level", 0)
    except:
        st.session_state.ventilation = 0

voc_value = st.slider("VOC [0–500]", 0, 500, 50)

vent_level = st.slider(
    "Poziom wentylacji (0–5)", 0, 5, st.session_state.ventilation
)

if st.button("📌 Ustaw wentylację"):
    try:
        # Wysyłamy wartość VOC, co ustawi automatycznie wentylację w backendzie
        requests.post(
            f"{API_URL_WEATHER}/voc/set",
            json={"voc": voc_value},
            timeout=2
        )
        # Pobieramy nowy poziom wentylacji z API
        vent_state = requests.get(f"{API_URL_SMART_HOME}/ventilation", timeout=2).json()
        st.session_state.ventilation = vent_state.get("ventilation_level", 0)
        st.success(f"Poziom wentylacji ustawiony na {st.session_state.ventilation} ✅")
    except Exception as e:
        st.error(f"Błąd: {e}")

st.write("Aktualny poziom wentylacji:", st.session_state.ventilation)

# ---------------- LIGHTING ----------------
st.header("💡 Oświetlenie")
if "light_on" not in st.session_state:
    st.session_state.light_on = False

auto_light = st.checkbox("Tryb automatyczny (światło włącza się gdy ciemno)")
if auto_light and weather:
    st.session_state.light_on = weather["sunlight_lux"] < 10000

if st.button("Przełącz światło"):
    st.session_state.light_on = not st.session_state.light_on

st.write("Stan:", "🔆 Włączone" if st.session_state.light_on else "🌑 Wyłączone")

# ---------------- HVAC ----------------
st.header("❄️ HVAC (Ogrzewanie/Chłodzenie)")
if "hvac_mode" not in st.session_state:
    st.session_state.hvac_mode = "AUTO"  # AUTO, HEAT, COOL, OFF

hvac_mode = st.radio("Tryb HVAC", ["AUTO", "HEAT", "COOL", "OFF"], index=0)

hvac_status = "❌ Wyłączone"
if weather:
    temp = weather["temperature"]
    if hvac_mode == "HEAT" or (hvac_mode == "AUTO" and temp < 20):
        hvac_status = "🔥 Ogrzewanie"
    elif hvac_mode == "COOL" or (hvac_mode == "AUTO" and temp > 25):
        hvac_status = "❄️ Chłodzenie"
    else:
        hvac_status = "⏸ Wentylacja"
st.write("Status:", hvac_status)

# ---------------- MONITORING / ACCESS / ROOMS ----------------
st.header("📹 Monitoring / Alarm / Zamek")
if "alarm_on" not in st.session_state:
    st.session_state.alarm_on = False
if st.button("Przełącz alarm"):
    st.session_state.alarm_on = not st.session_state.alarm_on
st.write("Stan:", "🚨 Alarm aktywny" if st.session_state.alarm_on else "✅ Alarm wyłączony")

if "door_locked" not in st.session_state:
    st.session_state.door_locked = True
if st.button("Przełącz zamek"):
    st.session_state.door_locked = not st.session_state.door_locked
st.write("Stan drzwi:", "🔒 Zamknięte" if st.session_state.door_locked else "🔓 Otwarte")

# ---------------- BLINDS ----------------
st.header("🪟 Rolety zewnętrzne")
rooms = ["Pokój dziecka 1", "Pokój dziecka 2", "Salon", "Sypialnia", "Kuchnia", "Łazienka"]

if "blinds" not in st.session_state:
    st.session_state.blinds = {room: 0 for room in rooms}

if weather:
    for room in rooms:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.write(f"**{room}**")
            # automatyczna logika
            wind = weather["wind_kph"]
            sun = weather["sunlight_lux"]
            temp = weather["temperature"]
            auto_level = None
            if wind > 40:
                auto_level = 100
            elif temp < 10 and sun > 15000:
                auto_level = 0
            elif temp > 25 and sun > 20000:
                auto_level = 70
            if auto_level is not None:
                st.session_state.blinds[room] = auto_level
                st.write("🤖 Tryb automatyczny:", auto_level, "%")
            # manual slider
            st.session_state.blinds[room] = st.slider(
                f"Ustaw rolety ({room})",
                0, 100, st.session_state.blinds[room],
                step=10, key=f"blind_{room}"
            )

        with col2:
            level = st.session_state.blinds[room]
            st.metric("Poziom rolet", f"{level}%")
            if level == 0:
                st.write("🌞 Otwarte")
            elif level == 100:
                st.write("🌑 Zamknięte")
            else:
                st.write("🌗 Częściowo przysłonięte")
