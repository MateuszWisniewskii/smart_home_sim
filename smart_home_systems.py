class SmartHomeSystems:
    # progi dla automatycznych zachowań
    WIND_LIMIT = 80                # km/h
    COLD_TEMP_THRESHOLD = 10       # °C – poniżej tej temp. jest zimno
    SUN_LUX_THRESHOLD = 20000      # lux – powyżej jest słonecznie
    MAX_SUN_HEAT_POSITION = 30     # maksymalne opuszczenie rolety w zimno-słonecznie

    HOT_TEMP_THRESHOLD = 28        # °C – powyżej tej temp. jest gorąco
    HOT_SUN_LUX_THRESHOLD = 30000  # lux – powyżej jest bardzo słonecznie
    HOT_MIN_POSITION = 70          # minimalne opuszczenie rolety w gorąco-słonecznie

    def __init__(self):
        # rolety w procentach: 0 = zamknięta, 100 = otwarta
        self.blinds = {
            "living_room": 0,
            "bedroom": 0,
            "kitchen": 0
        }
        # lamele w procentach: 0 = zamknięte, 100 = całkowicie otwarte
        self.slats = {room: 50 for room in self.blinds}
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
                if self.blinds[room] > 30:
                    self.blinds[room] = 30

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
        return {
            "blinds": self.blinds.copy(),
            "slats": self.slats.copy(),
            "wind_limit_active": self.current_wind >= self.WIND_LIMIT,
            "cold_sunny_limit_active": self.current_temp < self.COLD_TEMP_THRESHOLD
                                         and self.current_sunlight > self.SUN_LUX_THRESHOLD,
            "hot_sunny_limit_active": self.current_temp > self.HOT_TEMP_THRESHOLD
                                         and self.current_sunlight > self.HOT_SUN_LUX_THRESHOLD
        }
