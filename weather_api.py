from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from weather_simulator import WeatherSimulator
import uvicorn

app = FastAPI()
weather = WeatherSimulator()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/weather")
def get_weather():
    return weather.simulate_step()


@app.post("/weather/set")
def set_weather(params: dict):
    weather.set_manual(**params)
    return {"status": "ok", "mode": "manual", "state": weather.get_state()}


@app.post("/weather/auto")
def set_auto():
    weather.set_auto()
    return {"status": "ok", "mode": "auto"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)


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
