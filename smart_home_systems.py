class SmartHomeSystems:
    def __init__(self):
        # ---- progi automatyki (dynamiczne) ----
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
            "VOC_LEVEL_1": 200,
            "VOC_LEVEL_2": 300,
            "VOC_LEVEL_3": 400,
            "VOC_LEVEL_4": 500
        }

        # 🔹 Lista pokoi dynamiczna
        self.rooms = ["living_room", "bedroom", "kitchen"]

        # ---- stany urządzeń ----
        self.blinds = {room: 0 for room in self.rooms}
        self.slats = {room: 50 for room in self.rooms}
        self.lights = {room: 0 for room in self.rooms}
        self.ac = {room: False for room in self.rooms}
        self.ventilation = 0  # 🔹 Wentylacja 0–5

        # ---- aktualne warunki ----
        self.current_wind = 0
        self.current_temp = 20
        self.current_sunlight = 20000
        self.current_voc = 50

        # 🔒 flaga blokady automatyki
        self.manual_override = False

    # ---------------------- konfiguracja progów ----------------------
    def get_thresholds(self):
        return self.thresholds.copy()

    def set_thresholds(self, new_values: dict):
        for key, value in new_values.items():
            if key in self.thresholds:
                self.thresholds[key] = value
        return self.thresholds

    # ---------------------- Aktualizacja pogody ----------------------
    def update_weather(self, temperature: float, sunlight_lux: float, wind_kph: float, voc: float = None):
        self.current_temp = temperature
        self.current_sunlight = sunlight_lux
        self.current_wind = wind_kph
        if voc is not None:
            self.current_voc = voc

        if self.manual_override:
            return

        # 1️⃣ Blokada wiatrowa – rolety chowają się
        if self.current_wind >= self.thresholds["WIND_LIMIT"]:
            for room in self.blinds:
                self.blinds[room] = 0

        # 2️⃣ Zimno i słonecznie – rolety max
        elif self.current_temp < self.thresholds["COLD_TEMP_THRESHOLD"] and self.current_sunlight > self.thresholds["SUN_LUX_THRESHOLD"]:
            for room in self.blinds:
                self.blinds[room] = min(self.blinds[room], self.thresholds["MAX_SUN_HEAT_POSITION"])

        # 3️⃣ Gorąco i bardzo słonecznie – rolety min
        elif self.current_temp > self.thresholds["HOT_TEMP_THRESHOLD"] and self.current_sunlight > self.thresholds["HOT_SUN_LUX_THRESHOLD"]:
            for room in self.blinds:
                self.blinds[room] = max(self.blinds[room], self.thresholds["HOT_MIN_POSITION"])

        # 4️⃣ Bardzo jasno → światła gasną
        elif self.current_sunlight > self.thresholds["LIGHT_BRIGHT_THRESHOLD"]:
            for room in self.lights:
                self.lights[room] = 0

        # 5️⃣ Automatyczne włączenie klimatyzacji
        if self.current_temp > self.thresholds["AC_TEMP_LIMIT"]:
            for room in self.ac:
                self.ac[room] = True

        # 6️⃣ Automatyczne sterowanie wentylacją (0–5)
        if self.current_voc < self.thresholds["VOC_LEVEL_1"]:
            self.ventilation = 0
        elif self.current_voc < self.thresholds["VOC_LEVEL_2"]:
            self.ventilation = 2
        elif self.current_voc < self.thresholds["VOC_LEVEL_3"]:
            self.ventilation = 3
        elif self.current_voc < self.thresholds["VOC_LEVEL_4"]:
            self.ventilation = 4
        else:
            self.ventilation = 5

    # ---------------------- Rolety ----------------------
    def set_blind(self, room: str, position: int):
        if self.current_wind >= self.thresholds["WIND_LIMIT"]:
            return False
        if self.current_temp < self.thresholds["COLD_TEMP_THRESHOLD"] and self.current_sunlight > self.thresholds["SUN_LUX_THRESHOLD"]:
            position = min(position, self.thresholds["MAX_SUN_HEAT_POSITION"])
        if self.current_temp > self.thresholds["HOT_TEMP_THRESHOLD"] and self.current_sunlight > self.thresholds["HOT_SUN_LUX_THRESHOLD"]:
            position = max(position, self.thresholds["HOT_MIN_POSITION"])
        if room in self.blinds and 0 <= position <= 100:
            self.blinds[room] = position
            return True
        return False

    def adjust_blind(self, room: str, delta: int):
        if self.current_wind >= self.thresholds["WIND_LIMIT"]:
            return False
        if room in self.blinds:
            new_position = self.blinds[room] + delta
            if self.current_temp < self.thresholds["COLD_TEMP_THRESHOLD"] and self.current_sunlight > self.thresholds["SUN_LUX_THRESHOLD"]:
                new_position = min(new_position, self.thresholds["MAX_SUN_HEAT_POSITION"])
            if self.current_temp > self.thresholds["HOT_TEMP_THRESHOLD"] and self.current_sunlight > self.thresholds["HOT_SUN_LUX_THRESHOLD"]:
                new_position = max(new_position, self.thresholds["HOT_MIN_POSITION"])
            self.blinds[room] = max(0, min(100, new_position))
            return True
        return False

    # ---------------------- Światła ----------------------
    def set_light(self, room: str, brightness: int):
        if room in self.lights and 0 <= brightness <= 100:
            if self.current_sunlight > self.thresholds["LIGHT_BRIGHT_THRESHOLD"]:
                brightness = 0
            elif self.current_sunlight < self.thresholds["LIGHT_DARK_THRESHOLD"]:
                brightness = max(brightness, self.thresholds["LIGHT_MIN"])
            self.lights[room] = brightness
            return True
        return False

    def adjust_light(self, room: str, delta: int):
        if room in self.lights:
            new_brightness = self.lights[room] + delta
            if self.current_sunlight > self.thresholds["LIGHT_BRIGHT_THRESHOLD"]:
                new_brightness = 0
            elif self.current_sunlight < self.thresholds["LIGHT_DARK_THRESHOLD"]:
                new_brightness = max(new_brightness, self.thresholds["LIGHT_MIN"])
            self.lights[room] = max(0, min(100, new_brightness))
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

    # ---------------------- Lamele ----------------------
    def set_slats(self, room: str, angle: int):
        if self.current_wind >= self.thresholds["WIND_LIMIT"]:
            return False
        if room in self.slats and 0 <= angle <= 100:
            self.slats[room] = angle
            return True
        return False

    def adjust_slats(self, room: str, delta: int):
        if self.current_wind >= self.thresholds["WIND_LIMIT"]:
            return False
        if room in self.slats:
            new_angle = max(0, min(100, self.slats[room] + delta))
            self.slats[room] = new_angle
            return True
        return False

    # ---------------------- Wentylacja ----------------------
    def set_ventilation(self, level: int):
        """Ustaw ręcznie poziom wentylacji (0–5)."""
        if 0 <= level <= 5:
            self.ventilation = level
            return True
        return False

    def adjust_ventilation(self, delta: int):
        """Zwiększ/zmniejsz moc wentylacji."""
        new_level = max(0, min(5, self.ventilation + delta))
        self.ventilation = new_level
        return self.ventilation

    # ---------------------- tryb manualny ----------------------
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

    # ---------------------- Pobranie stanu ----------------------
    def get_state(self):
        return {
            "blinds": self.blinds.copy(),
            "slats": self.slats.copy(),
            "lights": self.lights.copy(),
            "ac": self.ac.copy(),
            "ventilation": self.ventilation,
            "manual_override": self.manual_override,
            "wind_limit_active": not self.manual_override and self.current_wind >= self.thresholds["WIND_LIMIT"],
            "cold_sunny_limit_active": not self.manual_override and self.current_temp < self.thresholds["COLD_TEMP_THRESHOLD"]
                                            and self.current_sunlight > self.thresholds["SUN_LUX_THRESHOLD"],
            "hot_sunny_limit_active": not self.manual_override and self.current_temp > self.thresholds["HOT_TEMP_THRESHOLD"]
                                            and self.current_sunlight > self.thresholds["HOT_SUN_LUX_THRESHOLD"],
            "light_limit_active": not self.manual_override and self.current_sunlight > self.thresholds["LIGHT_BRIGHT_THRESHOLD"],
            "ac_auto_active": not self.manual_override and self.current_temp > self.thresholds["AC_TEMP_LIMIT"],
            "ventilation_auto_level": None if self.manual_override else self.ventilation,
            "thresholds": self.get_thresholds()
        }
