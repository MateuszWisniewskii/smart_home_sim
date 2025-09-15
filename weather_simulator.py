import random
import time
from datetime import datetime


def clamp(v, a, b):
    return max(a, min(b, v))


class WeatherState:
    """Prosty obiekt przechowujący aktualny stan pogody."""

    def __init__(self,
                 temperature=22.0,
                 humidity=45.0,
                 wind_kph=5.0,
                 precipitation_mm=0.0,
                 cloud_pct=20.0,
                 sunlight_lux=20000.0):
        self.temperature = temperature
        self.humidity = humidity
        self.wind_kph = wind_kph
        self.precipitation_mm = precipitation_mm
        self.cloud_pct = cloud_pct
        self.sunlight_lux = sunlight_lux
        self.timestamp = datetime.now()

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "temperature": round(self.temperature, 2),
            "humidity": round(self.humidity, 2),
            "wind_kph": round(self.wind_kph, 2),
            "precipitation_mm": round(self.precipitation_mm, 2),
            "cloud_pct": round(self.cloud_pct, 2),
            "sunlight_lux": round(self.sunlight_lux, 2),
        }


class WeatherSimulator:
    """
    Generator pogody w czasie rzeczywistym.
    Możesz go używać do testów zamiast prawdziwych sensorów.
    """

    def __init__(self, mode="calm"):
        self.state = WeatherState()
        self.mode = mode
        self.manual_override = False
        self._last_update = time.time()

        self.mode_factors = {
            "calm": {"tempVar": 0.02, "cloudVar": 0.5, "rainProb": 0.01},
            "dynamic": {"tempVar": 0.2, "cloudVar": 3, "rainProb": 0.06},
            "storm": {"tempVar": 0.5, "cloudVar": 6, "rainProb": 0.2},
        }

    def step(self):
        """Aktualizuje pogodę w zależności od upływu czasu."""
        if self.manual_override:
            return self.state  # nie zmieniamy, gdy ręczny tryb włączony

        now = time.time()
        dt = now - self._last_update
        self._last_update = now

        mf = self.mode_factors.get(self.mode, self.mode_factors["calm"])
        s = self.state

        # temperatura
        s.temperature += (random.random() - 0.5) * mf["tempVar"] * dt * 10

        # wilgotność
        s.humidity += (random.random() - 0.5) * 1.5 * mf["tempVar"] * dt * 10
        s.humidity = clamp(s.humidity, 0, 100)

        # zachmurzenie
        s.cloud_pct += (random.random() - 0.5) * mf["cloudVar"] * dt
        s.cloud_pct = clamp(s.cloud_pct, 0, 100)

        # słońce (zależne od godziny i chmur)
        hour = datetime.now().hour
        is_day = 6 <= hour <= 20
        base_sun = 50000 if is_day else 0
        s.sunlight_lux = max(
            0,
            base_sun * (1 - s.cloud_pct / 100)
            + (random.random() - 0.5) * 2000
        )

        # wiatr
        s.wind_kph += (random.random() - 0.5) * 1.2 * dt
        s.wind_kph = clamp(s.wind_kph, 0, 150)

        # opady
        rain_chance = (s.cloud_pct / 100) * mf["rainProb"]
        if random.random() < rain_chance * dt:
            s.precipitation_mm = clamp(
                s.precipitation_mm + random.random() * 2 * dt * 60, 0, 100
            )
        else:
            s.precipitation_mm = max(0, s.precipitation_mm - 0.05 * dt)

        s.timestamp = datetime.now()
        return s

    def get_state(self):
        return self.state.to_dict()

    def set_state(self, **kwargs):
        """Ręczne nadpisanie wartości pogodowych."""
        for k, v in kwargs.items():
            if hasattr(self.state, k):
                setattr(self.state, k, v)
        self.manual_override = True
        self.state.timestamp = datetime.now()
