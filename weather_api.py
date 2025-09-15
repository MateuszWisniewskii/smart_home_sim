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
