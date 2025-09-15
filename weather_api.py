import asyncio
import uvicorn
from fastapi import FastAPI, Body
from weather_simulator import WeatherSimulator

app = FastAPI(title="Weather Sensor Simulator")

# globalny symulator
sim = WeatherSimulator(mode="dynamic")


@app.get("/weather")
def get_weather():
    """Zwraca aktualny stan pogody (ostatnia próbka)."""
    return sim.get_state()


@app.get("/weather/step")
def step_weather():
    """Wymusza krok symulacji i zwraca nowy stan."""
    state = sim.step()
    return state.to_dict()


@app.post("/weather/set")
def set_weather(params: dict = Body(...)):
    """Ręczne ustawienie parametrów pogodowych."""
    sim.set_state(**params)
    return sim.get_state()


@app.on_event("startup")
async def start_background_sim():
    """Startuje task, który co sekundę aktualizuje pogodę (jeśli nie ręczny tryb)."""
    async def loop():
        while True:
            sim.step()
            await asyncio.sleep(1)
    asyncio.create_task(loop())


if __name__ == "__main__":
    uvicorn.run("weather_api:app", host="0.0.0.0", port=8000, reload=True)
