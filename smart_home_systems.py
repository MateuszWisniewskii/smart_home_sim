class SmartHomeSystems:
    # progi dla automatycznych zachowań
    WIND_LIMIT = 80                # km/h
    COLD_TEMP_THRESHOLD = 10       # °C – poniżej tej temp. jest zimno
    SUN_LUX_THRESHOLD = 20000      # lux – powyżej jest słonecznie
    MAX_SUN_HEAT_POSITION = 30     # maksymalne opuszczenie rolety w zimno-słonecznie

    HOT_TEMP_THRESHOLD = 28        # °C – powyżej tej temp. jest gorąco
    FREEZING_TEMP_THRESHOLD = 18 
    HOT_SUN_LUX_THRESHOLD = 30000  # lux – powyżej jest bardzo słonecznie
    HOT_MIN_POSITION = 70          # minimalne opuszczenie rolety w gorąco-słonecznie

    LIGHT_BRIGHT_THRESHOLD = 30000 # lux – powyżej jest bardzo jasno
    LIGHT_MAX = 30                 # max jasność, gdy jasno
    LIGHT_DARK_THRESHOLD = 5000    # lux – poniżej jest ciemno
    LIGHT_MIN = 70                 # min jasność, gdy ciemno

    def __init__(self):
        # rolety w procentach: 0 = zamknięta, 100 = otwarta
        self.blinds = {
            "living_room": 0,
            "bedroom": 0,
            "kitchen": 0
        }
        # lamele w procentach: 0 = zamknięte, 100 = całkowicie otwarte
        self.slats = {room: 50 for room in self.blinds}
        # światła w procentach: 0 = zgaszone, 100 = pełna jasność
        self.lights = {room: 0 for room in self.blinds}
        # temperatura
        self.temperature = {room: 0 for room in self.blinds}
        # aktualny stan pogody
        self.current_wind = 0
        self.current_temp = 20
        self.current_sunlight = 20000

    # ---------------------- Aktualizacja pogody ----------------------
    def update_weather(self, temperature: float, sunlight_lux: float, wind_kph: float):
        """Aktualizacja pogody i automatyczne blokady/ograniczenia rolet."""
        self.current_temp = temperature
        self.current_sunlight = sunlight_lux
        self.current_wind = wind_kph

        # 1️⃣ Blokada wiatrowa – rolety max 30%
        if self.current_wind >= self.WIND_LIMIT:
            for room in self.blinds:
                if self.blinds[room] > 0:
                    self.blinds[room] = 0

        # 2️⃣ Zimno i słonecznie – rolety max 30%
        elif self.current_temp < self.COLD_TEMP_THRESHOLD and self.current_sunlight > self.SUN_LUX_THRESHOLD:
            for room in self.blinds:
                if self.blinds[room] > self.MAX_SUN_HEAT_POSITION:
                    self.blinds[room] = self.MAX_SUN_HEAT_POSITION

        # 3️⃣ Gorąco i bardzo słonecznie – rolety min. 70%
        elif self.current_temp > self.HOT_TEMP_THRESHOLD and self.current_sunlight > self.HOT_SUN_LUX_THRESHOLD:
            for room in self.blinds:
                if self.blinds[room] < self.HOT_MIN_POSITION:
                    self.blinds[room] = self.HOT_MIN_POSITION

            # 🌞 Bardzo jasno → światła gaśnie do 0%
        elif self.current_sunlight > self.LIGHT_BRIGHT_THRESHOLD:
            for room in self.lights:
                self.lights[room] = 0

    # ---------------------- Rolety góra-dół ----------------------
    def set_blind(self, room: str, position: int):
        """Ustawienie rolet w pozycji 0-100%."""
        if self.current_wind >= self.WIND_LIMIT:
            return False

        # zimno + słońce → max 30%
        if self.current_temp < self.COLD_TEMP_THRESHOLD and self.current_sunlight > self.SUN_LUX_THRESHOLD:
            position = min(position, self.MAX_SUN_HEAT_POSITION)

        # gorąco + słońce → min 70%
        if self.current_temp > self.HOT_TEMP_THRESHOLD and self.current_sunlight > self.HOT_SUN_LUX_THRESHOLD:
            position = max(position, self.HOT_MIN_POSITION)

        if room in self.blinds and 0 <= position <= 100:
            self.blinds[room] = position
            return True
        return False

    def adjust_blind(self, room: str, delta: int):
        """Zmiana stanu rolety o delta procentów (+/-)."""
        if self.current_wind >= self.WIND_LIMIT:
            return False

        if room in self.blinds:
            new_position = self.blinds[room] + delta

            # zimno + słońce → max 30%
            if self.current_temp < self.COLD_TEMP_THRESHOLD and self.current_sunlight > self.SUN_LUX_THRESHOLD:
                new_position = min(new_position, self.MAX_SUN_HEAT_POSITION)

            # gorąco + słońce → min 70%
            if self.current_temp > self.HOT_TEMP_THRESHOLD and self.current_sunlight > self.HOT_SUN_LUX_THRESHOLD:
                new_position = max(new_position, self.HOT_MIN_POSITION)

            self.blinds[room] = max(0, min(100, new_position))
            return True
        return False

# ----------------------------------------------- Światła --------------------------------------------------------
    def set_light(self, room: str, brightness: int):
        """Ustawienie jasności światła w 0-100%."""
        if room in self.lights and 0 <= brightness <= 100:
            # Bardzo jasno → światła gasną
            if self.current_sunlight > self.LIGHT_BRIGHT_THRESHOLD:
                brightness = 0
            # Bardzo ciemno → min 70%
            elif self.current_sunlight < self.LIGHT_DARK_THRESHOLD:
                brightness = max(brightness, self.LIGHT_MIN)

            self.lights[room] = brightness
            return True
        return False

    def adjust_light(self, room: str, delta: int):
        """Zmiana jasności światła o delta procentów (+/-)."""
        if room in self.lights:
            new_brightness = self.lights[room] + delta

            # Bardzo jasno → światła gasną
            if self.current_sunlight > self.LIGHT_BRIGHT_THRESHOLD:
                new_brightness = 0
            # Bardzo ciemno → min 70%
            elif self.current_sunlight < self.LIGHT_DARK_THRESHOLD:
                new_brightness = max(new_brightness, self.LIGHT_MIN)

            self.lights[room] = max(0, min(100, new_brightness))
            return True
        return False
    
    # ----------------------------------------------- Klimatyzacja --------------------------------------------------------
    def set_aircon(self, room: str, temperature: int):
        """Ustawienie jasności światła w 0-100%."""
        if room in self.lights and 0 <= temperature <= 100:
            # Bardzo jasno → światła gasną
            if self.current_sunlight > self.LIGHT_BRIGHT_THRESHOLD:
                temperature = 0
            # Bardzo ciemno → min 70%
            elif self.current_sunlight < self.LIGHT_DARK_THRESHOLD:
                temperature = max(temperature, self.LIGHT_MIN)

            self.temperature[room] = temperature
            return True
        return False

    def adjust_aircon(self, room: str, delta: int):
        """Zmiana jasności światła o delta procentów (+/-)."""
        if room in self.lights:
            new_brightness = self.lights[room] + delta

            # Bardzo jasno → światła gasną
            if self.current_sunlight > self.LIGHT_BRIGHT_THRESHOLD:
                new_brightness = 0
            # Bardzo ciemno → min 70%
            elif self.current_sunlight < self.LIGHT_DARK_THRESHOLD:
                new_brightness = max(new_brightness, self.LIGHT_MIN)

            self.lights[room] = max(0, min(100, new_brightness))
            return True
        return False
    
    # ---------------------- Lamele ----------------------
    def set_slats(self, room: str, angle: int):
        """Ustawienie kąta lameli 0-100%."""
        if self.current_wind >= self.WIND_LIMIT:
            return False
        if room in self.slats and 0 <= angle <= 100:
            self.slats[room] = angle
            return True
        return False

    def adjust_slats(self, room: str, delta: int):
        """Zmiana kąta lameli o delta procentów."""
        if self.current_wind >= self.WIND_LIMIT:
            return False
        if room in self.slats:
            new_angle = max(0, min(100, self.slats[room] + delta))
            self.slats[room] = new_angle
            return True
        return False

    # ---------------------- Pobranie stanu ----------------------
    def get_state(self):
        light_limit_active = self.current_sunlight > self.LIGHT_BRIGHT_THRESHOLD
        return {
            "blinds": self.blinds.copy(),
            "slats": self.slats.copy(),
            "lights": self.lights.copy(),
            "wind_limit_active": self.current_wind >= self.WIND_LIMIT,
            "cold_sunny_limit_active": self.current_temp < self.COLD_TEMP_THRESHOLD
                                        and self.current_sunlight > self.SUN_LUX_THRESHOLD,
            "hot_sunny_limit_active": self.current_temp > self.HOT_TEMP_THRESHOLD
                                        and self.current_sunlight > self.HOT_SUN_LUX_THRESHOLD,
            "light_limit_active": light_limit_active
        }
