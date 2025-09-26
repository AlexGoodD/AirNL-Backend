from fastapi import APIRouter
import httpx
from app.services.aqi_compute import compute_aqi_pm25
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/forecast")
async def forecast_air(lat: float, lon: float, hours: int = 12):
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=pm2_5&timezone=America%2FMonterrey"
        f"&past_days=1"  # 👈 importante: incluye datos de ayer hasta ahora
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data = resp.json()

    pm25_series = data.get("hourly", {}).get("pm2_5", [])
    times = data.get("hourly", {}).get("time", [])

    # Junta series en pares (valor, timestamp)
    pairs = [
        (val, ts) for val, ts in zip(pm25_series, times)
        if val is not None
    ]

    # 👇 Ahora filtras: la hora actual y N horas hacia atrás
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    series = []
    for i in range(hours):
        target_time = now - timedelta(hours=i)
        for val, ts in pairs:
            if ts == target_time.strftime("%Y-%m-%dT%H:00"):
                aqi, category = compute_aqi_pm25(val)
                series.append({
                    "ts": ts,
                    "pollutant": "PM2.5",
                    "value": val,
                    "aqi": aqi,
                    "category": category,
                    "source": "OpenMeteo"
                })
                break

    return {
        "location": {"lat": lat, "lon": lon},
        "horizon_hours": hours,
        "series": sorted(series, key=lambda x: x["ts"], reverse=True)
    }