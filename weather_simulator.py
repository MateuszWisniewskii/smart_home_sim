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
        self.current_time = datetime.now()

    def get_state(self):
        return {
            "time": self.current_time.strftime("%Y-%m-%d %H:%M"),
            "temperature": round(self.temperature, 1),
            "humidity": round(self.humidity, 1),
            "cloud_pct": round(self.cloud_pct, 1),
            "sunlight_lux": round(self.sunlight_lux, 0),
            "wind_kph": round(self.wind_kph, 1),
            "precipitation_mm": round(self.precipitation_mm, 1),
        }

    def set_weather(self, **kwargs):
        """Ustaw parametry pogody ręcznie."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def set_time(self, hour: int, minute: int = 0):
        """Ustaw ręcznie godzinę w symulacji."""
        self.current_time = self.current_time.replace(hour=hour, minute=minute)

    def shift_time(self, hours: int = 0, minutes: int = 0):
        """Przesuń czas o podaną ilość godzin/minut."""
        self.current_time += timedelta(hours=hours, minutes=minutes)

