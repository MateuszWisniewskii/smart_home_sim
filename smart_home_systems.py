class SmartHomeSystems:
    def __init__(self):
        # rolety w procentach: 0 = zamknięta, 100 = otwarta
        self.blinds = {
            "living_room": 0,
            "bedroom": 0,
            "kitchen": 0
        }

    def set_blind(self, room: str, position: int):
        """Ustawienie rolet w pozycji 0-100%."""
        if room in self.blinds and 0 <= position <= 100:
            self.blinds[room] = position
            return True
        return False

    def adjust_blind(self, room: str, delta: int):
        """Zmiana stanu rolety o delta procentów (+/-)."""
        if room in self.blinds:
            new_position = max(0, min(100, self.blinds[room] + delta))
            self.blinds[room] = new_position
            return True
        return False

    def get_state(self):
        return {"blinds": self.blinds.copy()}
