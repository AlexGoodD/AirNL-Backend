import httpx

async def reverse_geocode(lat: float, lon: float, client: httpx.AsyncClient) -> str:
    """
    Resuelve un par (lat, lon) en una ubicación legible como
    'Monterrey, Nuevo León' usando Nominatim (OpenStreetMap).
    """
    url = (
        f"https://nominatim.openstreetmap.org/reverse"
        f"?lat={lat}&lon={lon}&format=json&zoom=10&addressdetails=1"
    )
    resp = await client.get(url, headers={"User-Agent": "AirNL/1.0"})
    if resp.status_code != 200:
        return "Unknown"

    data = resp.json()
    address = data.get("address", {})
    city = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
    )
    state = address.get("state")

    if city and state:
        return f"{city}, {state}"
    return city or state or "Unknown"