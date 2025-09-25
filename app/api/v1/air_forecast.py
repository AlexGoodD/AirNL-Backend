from fastapi import APIRouter
import httpx
from app.services.aqi_compute import compute_aqi_pm25

router = APIRouter()

@router.get("/forecast")
async def forecast_air(lat: float, lon: float, hours: int = 12):
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=pm2_5&timezone=America%2FMonterrey"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()

    pm25_series = data.get("hourly", {}).get("pm2_5", [])
    times = data.get("hourly", {}).get("time", [])

    series = []
    for val, ts in zip(pm25_series, times):
        if val is None:
            continue
        aqi, category = compute_aqi_pm25(val)
        series.append({
            "ts": ts,
            "pollutant": "pm25",
            "value": val,
            "aqi": aqi,
            "category": category,
            "source": "OpenMeteo"
        })

    return {
        "location": {"lat": lat, "lon": lon},
        "horizon_hours": hours,
        "series": series[:hours]
    }