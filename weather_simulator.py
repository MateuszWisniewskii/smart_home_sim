import random
from datetime import datetime, timedelta


class WeatherSimulator:
    def __init__(self):
        self.temperature = 20.0
        self.humidity = 50.0
        self.cloud_pct = 20.0
        self.sunlight_lux = 20000
        self.wind_kph = 5.0
        self.precipitation_mm = 0.0
        self.manual_override = False
        self.current_time = datetime.now()

    def simulate_step(self):
        """Symulacja kroku czasu (działa tylko, jeśli nie jest w trybie ręcznym)."""
        if self.manual_override:
            return self.get_state()

        self.current_time += timedelta(minutes=10)
        hour = self.current_time.hour

        # temperatura
        base_temp = 15 + 10 * (1 if 10 < hour < 18 else -1)
        self.temperature = base_temp + random.uniform(-2, 2)

        # wilgotność
        self.humidity = max(0, min(100, self.humidity + random.uniform(-2, 2)))

        # chmury
        self.cloud_pct = max(0, min(100, self.cloud_pct + random.uniform(-5, 5)))

        # światło zależne od godziny i chmur
        if 6 <= hour <= 18:
            self.sunlight_lux = max(
                0, 50000 * (1 - self.cloud_pct / 100) + random.uniform(-1000, 1000)
            )
        else:
            self.sunlight_lux = 0

        # wiatr
        self.wind_kph = max(0, self.wind_kph + random.uniform(-1, 1))

        # opady
        if self.cloud_pct > 70:
            self.precipitation_mm = max(0, self.precipitation_mm + random.uniform(0, 1))
        else:
            self.precipitation_mm = max(0, self.precipitation_mm - 0.2)

        return self.get_state()

    def get_state(self):
        return {
            "time": self.current_time.strftime("%Y-%m-%d %H:%M"),
            "temperature": round(self.temperature, 1),
            "humidity": round(self.humidity, 1),
            "cloud_pct": round(self.cloud_pct, 1),
            "sunlight_lux": round(self.sunlight_lux, 0),
            "wind_kph": round(self.wind_kph, 1),
            "precipitation_mm": round(self.precipitation_mm, 1),
            "manual_override": self.manual_override,
        }

    def set_manual(self, **kwargs):
        """Ustaw parametry ręcznie i włącz tryb ręczny."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.manual_override = True

    def set_auto(self):
        """Wyłącz tryb ręczny, włącz symulację automatyczną."""
        self.manual_override = False
