from fastapi import APIRouter
import httpx
import asyncio
from app.services.aqi_compute import compute_aqi_pm25

router = APIRouter()

@router.get("/current")
async def current_air(lat: float, lon: float):
    air_url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}"
        "&hourly=pm2_5,pm10,ozone&timezone=America%2FMonterrey"
    )
    weather_url = (
        "https://api.open-meteo.com/v1/forecast?"
        f"latitude={lat}&longitude={lon}"
        "&hourly=relativehumidity_2m,windspeed_10m&timezone=America%2FMonterrey"
    )

    async with httpx.AsyncClient() as client:
        air_resp, weather_resp = await asyncio.gather(
            client.get(air_url),
            client.get(weather_url),
        )
        air_data = air_resp.json()
        weather_data = weather_resp.json()

    # --- AQI ---
    pm25_series = air_data.get("hourly", {}).get("pm2_5", [])
    times = air_data.get("hourly", {}).get("time", [])
    pm25_value, timestamp = None, None
    for val, ts in zip(reversed(pm25_series), reversed(times)):
        if val is not None:
            pm25_value, timestamp = val, ts
            break
    if pm25_value is None:
        return {"error": "No hay datos de PM2.5"}
    aqi, category = compute_aqi_pm25(pm25_value)

    # --- Weather ---
    humidity_series = weather_data.get("hourly", {}).get("relativehumidity_2m", [])
    wind_series = weather_data.get("hourly", {}).get("windspeed_10m", [])
    weather_times = weather_data.get("hourly", {}).get("time", [])

    humidity, wind_speed = None, None
    for h, w, ts in zip(reversed(humidity_series), reversed(wind_series), reversed(weather_times)):
        if h is not None and w is not None:
            humidity, wind_speed = h, w
            break

    return {
        "pollutant": "PM2.5",
        "value": pm25_value,
        "aqi": aqi,
        "category": category,
        "timestamp": timestamp,
        "source": "OpenMeteo",
        "humidity": humidity,
        "wind_speed": wind_speed
    }