import httpx
import asyncio
from fastapi import APIRouter
from app.settings import OPENAQ_API_KEY
from app.services.aqi_compute import compute_aqi_pm25
from app.services.geocode import reverse_geocode  

router = APIRouter()

async def fetch_openmeteo(lat: float, lon: float, client: httpx.AsyncClient):
    air_url = (
        "https://air-quality-api.open-meteo.com/v1/air-quality?"
        f"latitude={lat}&longitude={lon}"
        "&hourly=pm2_5&timezone=America%2FMonterrey"
    )
    air_resp = await client.get(air_url)
    air_data = air_resp.json()

    pm25_series = air_data.get("hourly", {}).get("pm2_5", [])
    times = air_data.get("hourly", {}).get("time", [])

    for val, ts in zip(reversed(pm25_series), reversed(times)):
        if val is not None:
            aqi, category = compute_aqi_pm25(val)
            return val, aqi, category, ts

    return None, 0, "No data", None


@router.get("/stations")
async def list_stations(lat: float, lon: float):
    url = f"https://api.openaq.org/v3/locations?coordinates={lat},{lon}&radius=20000&limit=10"
    headers = {"X-API-Key": OPENAQ_API_KEY}
    stations = []

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers)
        data = resp.json()

        tasks = []
        for loc in data.get("results", []):
            coords = loc.get("coordinates", {})
            lat_s = coords.get("latitude")
            lon_s = coords.get("longitude")

            if lat_s and lon_s:
                tasks.append(fetch_openmeteo(lat_s, lon_s, client))

        results = await asyncio.gather(*tasks)

        for loc, result in zip(data.get("results", []), results):
            pm25, aqi, category, updated = result
            coords = loc.get("coordinates", {})
            lat_s, lon_s = coords.get("latitude"), coords.get("longitude")

            location_name = await reverse_geocode(lat_s, lon_s, client)

            stations.append({
                "id": loc.get("id"),
                "name": loc.get("name"),
                "location": location_name,
                "distance": loc.get("distance"),
                "aqi": aqi,
                "category": category,
                "updated": updated,
                "lat": lat_s,
                "lon": lon_s,
            })

    return stations