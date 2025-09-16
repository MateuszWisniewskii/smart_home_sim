class SmartHomeSystems:
    def __init__(self):
        self.blinds = {
            "living_room": 0,
            "bedroom": 0,
            "kitchen": 0
        }
        self.wind_limit = 80
        self.current_wind = 0

    def update_wind(self, wind_speed: float):
        self.current_wind = wind_speed
        # automatycznie schowaj rolety do bezpiecznej pozycji jeśli wiatr ≥ limit
        if self.current_wind >= self.wind_limit:
            for room in self.blinds:
                if self.blinds[room] > 30:  # np. maksymalnie 30% odsłonięte
                    self.blinds[room] = 0

    def set_blind(self, room: str, position: int):
        # jeśli wiatr ≥ limit, użytkownik nie może zmienić pozycji
        if self.current_wind >= self.wind_limit:
            return False
        if room in self.blinds and 0 <= position <= 100:
            self.blinds[room] = position
            return True
        return False

    def adjust_blind(self, room: str, delta: int):
        if self.current_wind >= self.wind_limit:
            return False
        if room in self.blinds:
            new_position = max(0, min(100, self.blinds[room] + delta))
            self.blinds[room] = new_position
            return True
        return False

    def get_state(self):
        return {
            "blinds": self.blinds.copy(),
            "wind_limit_active": self.current_wind >= self.wind_limit
        }
