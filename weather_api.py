from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# ------------------ Smart Home System ------------------
class SmartHomeSystems:
    def __init__(self):
        # ---- progi automatyki ----
        self.thresholds = {
            "WIND_LIMIT": 80,
            "COLD_TEMP_THRESHOLD": 10,
            "SUN_LUX_THRESHOLD": 20000,
            "MAX_SUN_HEAT_POSITION": 30,
            "HOT_TEMP_THRESHOLD": 28,
            "HOT_SUN_LUX_THRESHOLD": 30000,
            "HOT_MIN_POSITION": 70,
            "LIGHT_BRIGHT_THRESHOLD": 30000,
            "LIGHT_MAX": 30,
            "LIGHT_DARK_THRESHOLD": 5000,
            "LIGHT_MIN": 70,
            "AC_TEMP_LIMIT": 35,
            "VOC_LEVEL_1": 100,  # przykładowe progi VOC
            "VOC_LEVEL_2": 200,
            "VOC_LEVEL_3": 300,
            "VOC_LEVEL_4": 400,
            "VOC_MAX_LEVEL": 4
        }

        # 🔹 Lista pokoi
        self.rooms = ["living_room", "bedroom", "kitchen"]

        # ---- stany urządzeń ----
        self.blinds = {room: 0 for room in self.rooms}
        self.slats = {room: 50 for room in self.rooms}
        self.lights = {room: 0 for room in self.rooms}
        self.ac = {room: False for room in self.rooms}
        self.ventilation = 0
        self.ventilation_auto_level = 0

        # ---- pogoda / VOC ----
        self.current_wind = 0
        self.current_temp = 20
        self.current_sunlight = 20000
        self.current_voc = 0

        # 🔒 tryb manualny
        self.manual_override = False

    # ---------------------- Progowe i manual ----------------------
    def get_thresholds(self):
        return self.thresholds.copy()

    def set_thresholds(self, new_values: dict):
        for key, value in new_values.items():
            if key in self.thresholds:
                self.thresholds[key] = value
        return self.thresholds

    def set_manual_override(self, state: bool):
        self.manual_override = state
        return self.manual_override

    def toggle_manual_override(self):
        self.manual_override = not self.manual_override
        return self.manual_override

    # ---------------------- Pokoje ----------------------
    def get_rooms(self):
        return self.rooms.copy()

    def add_room(self, room: str):
        if room not in self.rooms:
            self.rooms.append(room)
            self.blinds[room] = 0
            self.slats[room] = 50
            self.lights[room] = 0
            self.ac[room] = False
        return self.get_rooms()

    def remove_room(self, room: str):
        if room in self.rooms:
            self.rooms.remove(room)
            self.blinds.pop(room, None)
            self.slats.pop(room, None)
            self.lights.pop(room, None)
            self.ac.pop(room, None)
        return self.get_rooms()

    # ---------------------- Rolety ----------------------
    def set_blind(self, room: str, position: int):
        if room in self.blinds and 0 <= position <= 100:
            self.blinds[room] = position
            return True
        return False

    def adjust_blind(self, room: str, delta: int):
        if room in self.blinds:
            self.blinds[room] = max(0, min(100, self.blinds[room] + delta))
            return True
        return False

    # ---------------------- Światła ----------------------
    def set_light(self, room: str, brightness: int):
        if room in self.lights and 0 <= brightness <= 100:
            self.lights[room] = brightness
            return True
        return False

    def adjust_light(self, room: str, delta: int):
        if room in self.lights:
            self.lights[room] = max(0, min(100, self.lights[room] + delta))
            return True
        return False

    # ---------------------- Klimatyzacja ----------------------
    def set_ac(self, room: str, state: bool):
        if room in self.ac:
            self.ac[room] = state
            return True
        return False

    def toggle_ac(self, room: str):
        if room in self.ac:
            self.ac[room] = not self.ac[room]
            return True
        return False

    # ---------------------- Wentylacja / VOC ----------------------
    def set_ventilation(self, level: int):
        self.ventilation = max(0, min(100, level))
        return True

    def adjust_ventilation(self, delta: int):
        self.ventilation = max(0, min(100, self.ventilation + delta))
        return self.ventilation

    def set_voc(self, voc: int):
        self.current_voc = voc
        if not self.manual_override:
            # automatyczne ustawienie wentylacji według progów
            if voc >= self.thresholds["VOC_LEVEL_4"]:
                self.ventilation_auto_level = 100
            elif voc >= self.thresholds["VOC_LEVEL_3"]:
                self.ventilation_auto_level = 75
            elif voc >= self.thresholds["VOC_LEVEL_2"]:
                self.ventilation_auto_level = 50
            elif voc >= self.thresholds["VOC_LEVEL_1"]:
                self.ventilation_auto_level = 25
            else:
                self.ventilation_auto_level = 0
            # jeśli automatyka włączona, ustaw fizyczny poziom
            self.ventilation = self.ventilation_auto_level

    # ---------------------- Stan systemu ----------------------
    def get_state(self):
        return {
            "blinds": self.blinds.copy(),
            "slats": self.slats.copy(),
            "lights": self.lights.copy(),
            "ac": self.ac.copy(),
            "ventilation": self.ventilation,
            "ventilation_auto_level": self.ventilation_auto_level,
            "manual_override": self.manual_override,
            "thresholds": self.get_thresholds()
        }

# ------------------ FastAPI ------------------
app = FastAPI()
smart_home = SmartHomeSystems()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------- SMART HOME ----------------------
@app.get("/smart_home")
def get_smart_home_state():
    return smart_home.get_state()

@app.get("/smart_home/ventilation")
def get_ventilation():
    state = smart_home.get_state()
    return {
        "ventilation_level": state["ventilation"],
        "ventilation_auto_level": state.get("ventilation_auto_level", state["ventilation"])
    }

@app.post("/smart_home/ventilation/set")
def set_ventilation(params: dict):
    level = params.get("level", 0)
    smart_home.set_ventilation(level)
    return {
        "status": "ok",
        "ventilation_level": smart_home.get_state()["ventilation"]
    }

@app.post("/smart_home/ventilation/adjust")
def adjust_ventilation(params: dict):
    delta = params.get("delta", 0)
    new_level = smart_home.adjust_ventilation(delta)
    return {
        "status": "ok",
        "ventilation_level": new_level
    }

# ---------------------- VOC ----------------------
@app.post("/weather/voc/set")
def set_voc(params: dict):
    voc = params.get("voc", 0)
    smart_home.set_voc(voc)
    state = smart_home.get_state()
    return {
        "status": "ok",
        "voc": voc,
        "ventilation_level": state["ventilation"],
        "ventilation_auto_level": state["ventilation_auto_level"]
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
