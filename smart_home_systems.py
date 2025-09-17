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
            "AC_TEMP_LIMIT": 35
        }

        # ---- stany urządzeń ----
        self.blinds = { "living_room": 0, "bedroom": 0, "kitchen": 0 }
        self.slats = {room: 50 for room in self.blinds}
        self.lights = {room: 0 for room in self.blinds}
        self.ac = {room: False for room in self.blinds}

        self.current_wind = 0
        self.current_temp = 20
        self.current_sunlight = 20000

    # ---------------------- konfiguracja progów ----------------------
    def get_thresholds(self):
        return self.thresholds.copy()

    def set_thresholds(self, new_values: dict):
        for key, value in new_values.items():
            if key in self.thresholds:
                self.thresholds[key] = value
        return self.thresholds

    # ---------------------- Aktualizacja pogody ----------------------
    def update_weather(self, temperature: float, sunlight_lux: float, wind_kph: float):
        self.current_temp = temperature
        self.current_sunlight = sunlight_lux
        self.current_wind = wind_kph

        # 1️⃣ Blokada wiatrowa – rolety chowają się
        if self.current_wind >= self.thresholds["WIND_LIMIT"]:
            for room in self.blinds:
                if self.blinds[room] > 0:
                    self.blinds[room] = 0

        # 2️⃣ Zimno i słonecznie – rolety max
        elif self.current_temp < self.thresholds["COLD_TEMP_THRESHOLD"] and self.current_sunlight > self.thresholds["SUN_LUX_THRESHOLD"]:
            for room in self.blinds:
                if self.blinds[room] > self.thresholds["MAX_SUN_HEAT_POSITION"]:
                    self.blinds[room] = self.thresholds["MAX_SUN_HEAT_POSITION"]

        # 3️⃣ Gorąco i bardzo słonecznie – rolety min
        elif self.current_temp > self.thresholds["HOT_TEMP_THRESHOLD"] and self.current_sunlight > self.thresholds["HOT_SUN_LUX_THRESHOLD"]:
            for room in self.blinds:
                if self.blinds[room] < self.thresholds["HOT_MIN_POSITION"]:
                    self.blinds[room] = self.thresholds["HOT_MIN_POSITION"]

        # 4️⃣ Bardzo jasno → światła gasną
        elif self.current_sunlight > self.thresholds["LIGHT_BRIGHT_THRESHOLD"]:
            for room in self.lights:
                self.lights[room] = 0

        # 5️⃣ Automatyczne włączenie klimatyzacji
        if self.current_temp > self.thresholds["AC_TEMP_LIMIT"]:
            for room in self.ac:
                if not self.ac[room]:
                    self.ac[room] = True

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

    # ---------------------- Pobranie stanu ----------------------
    def get_state(self):
        return {
            "blinds": self.blinds.copy(),
            "slats": self.slats.copy(),
            "lights": self.lights.copy(),
            "ac": self.ac.copy(),
            "wind_limit_active": self.current_wind >= self.thresholds["WIND_LIMIT"],
            "cold_sunny_limit_active": self.current_temp < self.thresholds["COLD_TEMP_THRESHOLD"]
                                        and self.current_sunlight > self.thresholds["SUN_LUX_THRESHOLD"],
            "hot_sunny_limit_active": self.current_temp > self.thresholds["HOT_TEMP_THRESHOLD"]
                                        and self.current_sunlight > self.thresholds["HOT_SUN_LUX_THRESHOLD"],
            "light_limit_active": self.current_sunlight > self.thresholds["LIGHT_BRIGHT_THRESHOLD"],
            "ac_auto_active": self.current_temp > self.thresholds["AC_TEMP_LIMIT"],
            "thresholds": self.get_thresholds()
        }
