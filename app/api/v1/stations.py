from fastapi import APIRouter

router = APIRouter()

@router.get("/stations")
async def list_stations(lat: float, lon: float):
    stations = [
        {
            "id": "s1",
            "name": "Monterrey Centro",
            "location": "Monterrey",
            "distance": "1.2 km",
            "aqi": 72,
            "category": "Moderate",
            "updated": "2025-09-25T12:00:00Z",
            "lat": 25.67,
            "lon": -100.31
        },
        {
            "id": "s2",
            "name": "San Nicolás",
            "location": "San Nicolás",
            "distance": "5.8 km",
            "aqi": 110,
            "category": "Unhealthy for Sensitive Groups",
            "updated": "2025-09-25T12:00:00Z",
            "lat": 25.75,
            "lon": -100.28
        }
    ]
    return stations