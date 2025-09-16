from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from weather_simulator import WeatherSimulator
import uvicorn
from smart_home_systems import SmartHomeSystems

app = FastAPI()
weather = WeatherSimulator()
smart_home = SmartHomeSystems()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/weather")
def get_weather():
    state = weather.get_state()
    # zamiast update_wind -> update_weather
    smart_home.update_weather(
        temperature=state["temperature"],
        sunlight_lux=state["sunlight_lux"],
        wind_kph=state["wind_kph"]
    )
    return state


@app.post("/weather/set")
def set_weather(params: dict):
    weather.set_weather(**params)
    return {"status": "ok", "state": weather.get_state()}

@app.post("/weather/time/set")
def set_time(params: dict):
    hour = params.get("hour", 12)
    minute = params.get("minute", 0)
    weather.set_time(hour, minute)
    return {"status": "ok", "time": weather.get_state()["time"]}

@app.post("/weather/time/shift")
def shift_time(params: dict):
    hours = params.get("hours", 0)
    minutes = params.get("minutes", 0)
    weather.shift_time(hours=hours, minutes=minutes)
    return {"status": "ok", "time": weather.get_state()["time"]}

@app.get("/smart_home")
def get_smart_home_state():
    return smart_home.get_state()

@app.post("/smart_home/blinds/set")
def set_blind(params: dict):
    room = params.get("room")
    position = params.get("position")  # "open" lub "closed"
    success = smart_home.set_blind(room, position)
    return {"status": "ok" if success else "error", "blinds": smart_home.get_state()["blinds"]}

@app.post("/smart_home/blinds/set")
def set_blind(params: dict):
    room = params.get("room")
    position = params.get("position")  # liczba 0-100
    success = smart_home.set_blind(room, position)
    return {"status": "ok" if success else "error", "blinds": smart_home.get_state()["blinds"]}

@app.post("/smart_home/blinds/adjust")
def adjust_blind(params: dict):
    room = params.get("room")
    delta = params.get("delta", 0)  # liczba dodatnia lub ujemna
    success = smart_home.adjust_blind(room, delta)
    return {"status": "ok" if success else "error", "blinds": smart_home.get_state()["blinds"]}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)

