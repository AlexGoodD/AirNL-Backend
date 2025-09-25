from fastapi import APIRouter
from app.services.aqi_compute import compute_aqi_pm25

router = APIRouter()

@router.post("/advice")
async def advice(data: dict):
    age_group = data.get("age_group", "adult")
    activity = data.get("activity", "commute")
    concentration = data.get("pm25", None)
    
    if concentration is None:
        return {"error": "pm25 value is required"}

    aqi, category = compute_aqi_pm25(concentration)

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
        msg = "Emergency conditions. Avoid all outdoor activity and stay indoors."
        severity = "critical"

    else:
        msg = "No advice available."
        severity = "unknown"

    return {
        "aqi": aqi,
        "category": category,
        "message": msg,
        "severity": severity
    }