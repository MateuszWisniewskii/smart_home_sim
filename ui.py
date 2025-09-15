import streamlit as st
import requests
import random
from datetime import datetime

API_URL = "http://127.0.0.1:8000/weather"

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

st.title("🏠 Smart Home Dashboard")

# ---------------- MANUAL CONTROL ----------------
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
            "http://127.0.0.1:8000/weather/set",
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
    weather = requests.get(API_URL, timeout=2).json()
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

    # ---------------- TEMPERATURE SENSORS ----------------
    st.subheader("🌡 Temperatury z różnych czujników")

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


# ---------------- MONITORING ----------------
st.header("📹 Monitoring / Alarm")
if "alarm_on" not in st.session_state:
    st.session_state.alarm_on = False

if st.button("Przełącz alarm"):
    st.session_state.alarm_on = not st.session_state.alarm_on

st.write("Stan:", "🚨 Alarm aktywny" if st.session_state.alarm_on else "✅ Alarm wyłączony")


# ---------------- ACCESS ----------------
st.header("🚪 Dostęp (Zamek)")
if "door_locked" not in st.session_state:
    st.session_state.door_locked = True

if st.button("Przełącz zamek"):
    st.session_state.door_locked = not st.session_state.door_locked

st.write("Stan drzwi:", "🔒 Zamknięte" if st.session_state.door_locked else "🔓 Otwarte")


# ---------------- ROOMS ----------------
st.header("🏠 Pokoje i czujniki")

rooms = ["Pokój dziecka 1", "Pokój dziecka 2", "Salon", "Sypialnia", "Kuchnia", "Łazienka"]

if weather:
    tabs = st.tabs(rooms)

    for i, room in enumerate(rooms):
        with tabs[i]:
            st.subheader(room)

            # Symulacja danych dla danego pokoju
            room_temp = weather["temperature"] + random.uniform(-2, 2)
            room_hum = weather["humidity"] + random.uniform(-5, 5)

            # Sesyjny stan dla światła i drzwi w danym pokoju
            key_light = f"light_{i}"
            key_door = f"door_{i}"
            if key_light not in st.session_state:
                st.session_state[key_light] = False
            if key_door not in st.session_state:
                st.session_state[key_door] = True

            col1, col2 = st.columns(2)
            col1.metric("🌡 Temperatura [°C]", round(room_temp, 1))
            col2.metric("💧 Wilgotność [%]", round(room_hum, 1))

            st.write("💡 Oświetlenie:", "🔆 Włączone" if st.session_state[key_light] else "🌑 Wyłączone")
            if st.button("Przełącz światło", key=f"btn_light_{i}"):
                st.session_state[key_light] = not st.session_state[key_light]

            st.write("🚪 Drzwi:", "🔒 Zamknięte" if st.session_state[key_door] else "🔓 Otwarte")
            if st.button("Przełącz drzwi", key=f"btn_door_{i}"):
                st.session_state[key_door] = not st.session_state[key_door]