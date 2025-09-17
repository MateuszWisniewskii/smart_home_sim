import streamlit as st
import requests
from streamlit_autorefresh import st_autorefresh

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Smart Home Dashboard", layout="wide")

# auto-refresh co 5 sek
st_autorefresh(interval=5000, key="refresh")

st.title("🏠 Smart Home Dashboard")

tab1, tab2 = st.tabs(["📊 Panel", "⚙️ Ustawienia progów"])

rooms = ["living_room", "bedroom", "kitchen"]

st.sidebar.header("⚙️ Ustawienia globalne")
try:
    state = requests.get(f"{API_URL}/smart_home", timeout=2).json()
    manual_override = state.get("manual_override", False)
except:
    manual_override = False

manual_state = st.sidebar.toggle("🔒 Tryb manualny (wyłącza automatykę)", value=manual_override)

if manual_state != manual_override:
    requests.post(f"{API_URL}/smart_home/manual_override/set", json={"state": manual_state})

if manual_state:
    st.sidebar.warning("Automatyka wyłączona – sterowanie tylko ręczne.")


# ---------------- TAB 1: PANEL ----------------
with tab1:
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
    st.header("🪟 Sterowanie roletami")
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
            st.warning("⚠️ Rolety zablokowane przy wietrze")
            st.slider("Pozycja [%]", 0, 100, current_position, key=f"{room}_slider", disabled=True)
        else:
            position = st.slider("Pozycja [%]", 0, 100, current_position, key=f"{room}_slider")
            if st.button(f"📌 Ustaw {room}", key=f"{room}_set"):
                requests.post(f"{API_URL}/smart_home/blinds/set", json={"room": room, "position": position})

    # ---------------- LIGHTS ----------------
    st.header("💡 Sterowanie światłami")
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
            st.info("ℹ️ Klimatyzacja automatycznie włączona (możesz ją wyłączyć).")

        ac_state = st.toggle("Klimatyzacja", value=ac_on, key=f"{room}_ac")
        if st.button(f"📌 Zmień AC {room}", key=f"{room}_ac_set"):
            requests.post(f"{API_URL}/smart_home/ac/set", json={"room": room, "state": ac_state})

# ---------------- TAB 2: THRESHOLDS ----------------
with tab2:
    st.header("⚙️ Konfiguracja progów automatyki")
    try:
        thresholds = requests.get(f"{API_URL}/smart_home/thresholds", timeout=2).json()
    except Exception as e:
        st.error(f"Błąd w pobieraniu progów: {e}")
        thresholds = {}

    if thresholds:
        new_wind = st.slider("💨 Limit wiatru [km/h]", 0, 150, thresholds["WIND_LIMIT"])
        new_ac = st.slider("❄️ Temp. klimatyzacji [°C]", 20, 45, thresholds["AC_TEMP_LIMIT"])
        new_hot_temp = st.slider("🌡 Temp. gorąco [°C]", 20, 40, thresholds["HOT_TEMP_THRESHOLD"])
        new_cold_temp = st.slider("🌡 Temp. zimno [°C]", -10, 20, thresholds["COLD_TEMP_THRESHOLD"])
        new_sun = st.slider("🌞 Lux słońca (zimno-słonecznie)", 0, 50000, thresholds["SUN_LUX_THRESHOLD"])
        new_light_bright = st.slider("💡 Lux jasne światło", 0, 50000, thresholds["LIGHT_BRIGHT_THRESHOLD"])

        if st.button("📌 Zapisz progi"):
            r = requests.post(
                f"{API_URL}/smart_home/thresholds/set",
                json={
                    "WIND_LIMIT": new_wind,
                    "AC_TEMP_LIMIT": new_ac,
                    "HOT_TEMP_THRESHOLD": new_hot_temp,
                    "COLD_TEMP_THRESHOLD": new_cold_temp,
                    "SUN_LUX_THRESHOLD": new_sun,
                    "LIGHT_BRIGHT_THRESHOLD": new_light_bright,
                },
                timeout=2,
            )
            if r.status_code == 200:
                st.success("Progi zapisane ✅")
            else:
                st.error(f"Błąd API: {r.text}")
