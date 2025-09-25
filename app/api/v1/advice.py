from fastapi import APIRouter
import httpx
from app.services.aqi_compute import compute_aqi_pm25

router = APIRouter()

@router.post("/advice")
async def advice(data: dict):
    age_group = data.get("age_group", "adult")
    activity = data.get("activity", "commute")
    location = data.get("location", {})

    lat = location.get("lat")
    lon = location.get("lon")

    if not lat or not lon:
        return {"error": "lat and lon are required"}

    # Llama a OpenMeteo para obtener PM2.5 actual
    url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}"
        "&hourly=pm2_5&timezone=auto"
    )
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        data_resp = resp.json()

    pm25_series = data_resp.get("hourly", {}).get("pm2_5", [])
    times = data_resp.get("hourly", {}).get("time", [])

    pm25_value = None
    timestamp = None
    for val, ts in zip(reversed(pm25_series), reversed(times)):
        if val is not None:
            pm25_value = val
            timestamp = ts
            break

    if pm25_value is None:
        return {"error": "No PM2.5 data available"}

    # Calcula AQI y categoría
    aqi, category = compute_aqi_pm25(pm25_value)

    # Lógica de recomendaciones
    if category == "Good":
        msg = "Air quality is good. Safe to enjoy outdoor activities."
        severity = "low"

    elif category == "Moderate":
        msg = "Air quality is acceptable. Sensitive groups should reduce long outdoor exertion."
        severity = "moderate"

    elif category == "Unhealthy for Sensitive Groups":
        if age_group in ["child", "elderly"]:
            msg = "Children and elderly should avoid prolonged outdoor activities."
        else:
            msg = "Sensitive individuals may feel effects. Limit outdoor exercise."
        severity = "moderate-high"

    elif category == "Unhealthy":
        if activity in ["run", "exercise"]:
            msg = "Avoid strenuous outdoor activity. Move exercises indoors."
        else:
            msg = "Air quality is unhealthy. Limit outdoor exposure."
        severity = "high"

    elif category == "Very Unhealthy":
        msg = "Health alert: everyone may experience serious effects. Stay indoors when possible."
        severity = "very-high"

    elif category == "Hazardous":
        msg = "Emergency conditions. Avoid all outdoor activity and remain indoors."
        severity = "critical"

    else:
        msg = "No advice available."
        severity = "unknown"

    return {
        "aqi": aqi,
        "category": category,
        "pollutant": "PM2.5",
        "value": pm25_value,
        "timestamp": timestamp,
        "message": msg,
        "severity": severity,
        "source": "OpenMeteo"
    }